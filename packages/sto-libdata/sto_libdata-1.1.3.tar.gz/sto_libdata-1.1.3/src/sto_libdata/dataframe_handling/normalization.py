from collections import defaultdict
from typing import Any, NamedTuple, Optional, cast

from sqlalchemy import ForeignKey
from sqlalchemy.types import TypeEngine as SQLType

from sto_libdata.dataframe_handling.pushable_dataframe import PushableDF

from .shared import DataFrame, NamedDataFrame


class TableAndColumnName(NamedTuple):
    table_name: str
    column_name: str


type TableColumnDictionary[T] = dict[str, dict[str, T]]
type ForeignKeyIndex = TableColumnDictionary[TableAndColumnName]
type ForeignKeyInvertedIndex = TableColumnDictionary[set[TableAndColumnName]]


class _ForeignKeyStateHandler:
    """Keep track of the foreign key relations in a NormalizationHandler.

    Intended to use only inside this module. The idea is to facilitate
    renaming of tables or columns by keeping an inverted index (not only
    where each foreign key points to, but also where each column is pointed
    from).
    """

    def __init__(self) -> None:
        self.__foreign_keys: ForeignKeyIndex = defaultdict(dict)
        self.__inverted_index: ForeignKeyInvertedIndex = defaultdict(
            lambda: defaultdict(set)
        )

    def add_foreign_key(
        self,
        origin_table: str,
        origin_column: str,
        destination_table: str,
        destination_column: str,
    ) -> None:
        self.__foreign_keys[origin_table][origin_column] = TableAndColumnName(
            destination_table,
            destination_column,
        )

        self.__inverted_index[destination_table][destination_column].add(
            TableAndColumnName(origin_table, origin_column)
        )

    def remove_foreign_key(self, origin_table: str, origin_column: str) -> None:
        if not origin_column in self.__foreign_keys[origin_table]:
            return

        fk = self.__foreign_keys[origin_table].pop(origin_column)

        destination_table = fk.table_name
        destination_column = fk.column_name

        self.__inverted_index[destination_table][destination_column].remove(
            TableAndColumnName(origin_table, origin_column)
        )

    def rename_column(self, table: str, old_name: str, new_name: str) -> None:
        if old_name in self.__foreign_keys[table].keys():
            pointed_table, pointed_column = self.__foreign_keys[table].pop(old_name)

            self.__foreign_keys[table][new_name] = TableAndColumnName(
                pointed_table,
                pointed_column,
            )

            self.__replace_in_inverted_index(
                pointed_table,
                pointed_column,
                TableAndColumnName(table, old_name),
                TableAndColumnName(table, new_name),
            )

        if old_name in self.__inverted_index[table].keys():
            self.__inverted_index[table][new_name] = self.__inverted_index[table].pop(
                old_name
            )

        for affected_table, affected_column in self.__inverted_index[table][new_name]:
            self.__foreign_keys[affected_table][affected_column] = TableAndColumnName(
                table, new_name
            )

    def rename_table(self, old_name: str, new_name: str) -> None:
        if old_name in self.__foreign_keys.keys():
            self.__foreign_keys[new_name] = self.__foreign_keys.pop(old_name)

        for pointing_column, (pointed_table, pointed_column) in self.__foreign_keys[
            new_name
        ].items():
            self.__replace_in_inverted_index(
                pointed_table,
                pointed_column,
                TableAndColumnName(old_name, pointing_column),
                TableAndColumnName(new_name, pointing_column),
            )

        self.__inverted_index[new_name] = self.__inverted_index.pop(old_name)

        for pointed_column, pointing_tables_and_columns in self.__inverted_index[
            new_name
        ].items():
            for pointing_table, pointing_column in pointing_tables_and_columns:
                self.__foreign_keys[pointing_table][pointing_column] = (
                    TableAndColumnName(
                        new_name,
                        pointed_column,
                    )
                )

    def __replace_in_inverted_index(
        self,
        table: str,
        column: str,
        old_names: TableAndColumnName,
        new_names: TableAndColumnName,
    ) -> None:
        self.__inverted_index[table][column] -= {old_names}
        self.__inverted_index[table][column].add(new_names)

    def get_foreign_keys(self) -> TableColumnDictionary[ForeignKey]:
        return {
            pointing_table: {
                pointing_column: ForeignKey(f"{pointed_table}.{pointed_column}")
                for pointing_column, (
                    pointed_table,
                    pointed_column,
                ) in foreign_keys.items()
            }
            for pointing_table, foreign_keys in self.__foreign_keys.items()
        }


class NormalizationHandler:
    """An interface to normalize a single dataframe into separate tables."""

    def __init__(self, *dataframes: NamedDataFrame) -> None:
        self.__original_named_dataframes = dataframes
        self.__initialize_state(*dataframes)

    def __initialize_state(self, *dataframes: NamedDataFrame) -> None:
        self.__table_state: dict[str, DataFrame] = {
            named_df.name: named_df.df for named_df in dataframes
        }
        self.__foreign_key_handler = _ForeignKeyStateHandler()

    def add_dataframes(self, *dataframes: NamedDataFrame):
        """Adds dataframes to the underlying state.

        These are NOT remembered when calling `reset_state` and should be
        added again if desired.
        """
        for ndf in dataframes:
            self.__table_state[ndf.name] = ndf.df

    def reset_state(self) -> None:
        self.__initialize_state(*self.__original_named_dataframes)

    def get_state(self) -> dict[str, DataFrame]:
        """Fetches all of the dataframes that have been extracted so far."""
        return self.__table_state

    def __extract_table(self, base: DataFrame, column_list: list[str]) -> DataFrame:
        """Extracts and deduplicates a list of columns from a `base` dataset.

        Does not mutate the base dataset.
        """
        new_table = base[column_list].dropna(how="all").drop_duplicates().copy()

        new_table.reset_index(drop=True, inplace=True)
        new_table["ID"] = new_table.index + 1

        return cast(DataFrame, new_table)

    def __replace_columns_by_fk(
        self,
        base: DataFrame,
        base_name: str,
        dim: DataFrame,
        dim_name: str,
        join_columns: list[str],
        fk_column_name: str,
    ) -> DataFrame:
        """Replaces a set of columns in `base` by a foreign key to `dim`.

        This foreign key is computed by inner joining the two datasets on
        `column_list`. Therefore, names in `column_list` should be present on
        both dataframes.

        Does not mutate any of the datasets.
        """

        merged = base.merge(
            dim, on=join_columns, suffixes=(f"_{base_name}", f"_{dim_name}"), how="left"
        ).rename(columns={f"ID_{dim_name}": fk_column_name, f"ID_{base_name}": "ID"})

        all_columns = set(merged.columns)

        columns_to_keep = list(all_columns - set(join_columns))

        merged = cast(DataFrame, merged[columns_to_keep])

        return merged

    def extract_new_table(
        self,
        from_table: str,
        columns: set[str],
        new_table_name: str,
        new_column_name: Optional[str] = None,
    ) -> None:
        """Extracts a new table from a set of columns of the main dataframe.

        This method takes a set of columns of the main dataframe and creates a
        separate dataframe with them without duplicate rows. These columns are
        replaced from the main dataframe by a single foreign key column to the
        newly created dataframe.

        Keeps track of the newly created foreign key relation by storing it in
        an internal attribute.

        Args:
            from_table: The table from which to extract the columns.
            columns: The set of columns from which to extract a new dataframe.
            new_table_name: The name that the SQL table corresponding to the
                newly created dataframe should have in the database. If a table
                with this name already exists in this NormalizationHandler's
                state, it is overridden.
            new_column_name: The name that the column containing the foreign key
                to the newly created table should have in the main table. If
                None, a custom heuristic is used to extract the name: remove,
                if any, the prefix of `new_table_name` and prepend "ID_" to it.
        """
        if new_column_name is None:
            new_column_name = f"ID_{new_table_name.split('_', 1)[-1]}"

        column_list = list(columns)

        base_df = self.__table_state[from_table]

        new_table = self.__extract_table(base_df, column_list)

        substituted_table = self.__replace_columns_by_fk(
            base_df, from_table, new_table, new_table_name, column_list, new_column_name
        )

        self.__table_state[from_table] = substituted_table.copy()
        self.__table_state[new_table_name] = new_table.copy()

        self.__foreign_key_handler.add_foreign_key(
            from_table,
            new_column_name,
            new_table_name,
            "ID",
        )

    def swap_column_values(
        self,
        exchange_table: str,
        exchange_column: str,
        key_table: str,
        key_column: str,
        new_column: str = "ID",
        set_foreign_key: bool = True,
    ) -> None:
        """Swaps the contents of a column for the contents of another.

        This is intended to automate the common operation of trying to mark
        a relation between tables by something other than its primary key.
        That is, to avoid setting a foreign key to a column other than the
        primary key.

        For example, consider the following scenario: suppose that one has
        a set of registers per country, let's call it A, and wishes to persist
        this relation in the database via a foreign key to a "Country" table
        from A. The information about the countries in A, however, is codified
        in some way different from the primary key of Country; for instance,
        one has the ISO3166 code instead of the integral ID used in Country.
        Supposing that Country has a column for this ISO3166, it would be
        possible to annotate a foreign key to said column instead of the ID in
        Country; but it may be preferred to instead use the ID in Country
        directly. It is possible to get this ID via a JOIN operation (merge in
        pandas) on the ISO3166 column, and then drop it afterwards, but that is
        somewhat cumbersome. This is what this method automates.

        Args:
            exchange_table: The name of the dataframe to perform the exchange
                on. This would be the "A" table in the example above.
            exchange_column: The name of the column in the table to be
                exchanged. This would be the column containing the ISO3166 codes
                in A in the example above.
            key_table: The name of the table containing the mapping necessary
                for the exchange. This would be the "Country" table in the
                example above.
            key_column: The name of the column in the mapping table containing
                the "unwanted" information. This would be the column in Country
                containing the ISO3166 codes in the example above.
            new_column: The name of the column in the mapping table containing
                the desired informatoin. This would be the ID column in Country
                in the example above. Defaults to "ID".
            set_foreign_key: Whether to register a foreign key from the
                exchanged column to the new column. Also deletes any previously
                registered foreign key from the exchanged column. Defaults to
                True.
        """

        to_exchange_string = "_____TO EXCHANGE_____"
        to_exchange_key_column = to_exchange_string + key_column
        to_exchange_new_column = to_exchange_string + new_column
        exchange_df = self.__table_state[exchange_table]
        key_df = self.__table_state[key_table].rename(columns={
            key_column:to_exchange_key_column,
            new_column:to_exchange_new_column
        })

        # exchange_df_columns = set(exchange_df.columns)

        exchange_df = (
            exchange_df.merge(
                key_df[[to_exchange_key_column, to_exchange_new_column]],
                left_on=exchange_column,
                right_on=to_exchange_key_column,
                how="left",
            )
            .drop(columns=[to_exchange_key_column, exchange_column])
            .rename(
                columns={
                    to_exchange_new_column: exchange_column,
                }
            )
        )

        self.__table_state[exchange_table] = exchange_df
        if set_foreign_key:
            self.__foreign_key_handler.remove_foreign_key(
                exchange_table, exchange_column
            )
            self.__foreign_key_handler.add_foreign_key(
                exchange_table, exchange_column, key_table, new_column
            )

    def __assert_table_existence(self, name: str) -> None:
        if name not in self.__table_state.keys():
            raise KeyError(f"{name} is not among the current dataframes!")

    def __assert_column_existence(self, table: str, name: str) -> None:
        self.__assert_table_existence(table)

        if name not in self.__table_state[table].columns:
            raise KeyError(f"{name} is not a column of {table}!")

    def rename_table(self, old_name: str, new_name: str) -> None:
        """Rename a table inside the current instance.

        This effectively changes the name of the table in all internal
        attributes, so that when the instance is exported (for example,
        to PushableDataframes), the name of the table and all foreign
        keys related to it (both incoming and outgoing) are correctly
        updated.
        """

        self.__assert_table_existence(old_name)

        self.__table_state[new_name] = self.__table_state.pop(old_name)
        self.__foreign_key_handler.rename_table(old_name, new_name)

    def rename_column(self, table: str, old_name: str, new_name: str) -> None:
        """Rename a column of a table inside the current instance.

        This effectively changes the name of the column in all internal
        attributes, so that when the instance is exported (for example,
        to PushableDataframes), the name of the column and all foreign
        keys related to it (both incoming and outgoing) are correctly
        updated.
        """

        self.__assert_column_existence(table, old_name)

        self.__table_state[table] = self.__table_state[table].rename(
            columns={old_name: new_name}
        )

        self.__foreign_key_handler.rename_column(table, old_name, new_name)

    def get_foreign_keys(self) -> TableColumnDictionary[ForeignKey]:
        return self.__foreign_key_handler.get_foreign_keys()

    def __entry_to_pdf(
        self,
        entry_name: str,
        coltypes: dict[str, SQLType],
        constraints: dict[str, dict[str, Any]],
        foreign_keys: dict[str, ForeignKey],
    ) -> PushableDF:
        return PushableDF(
            df=self.__table_state[entry_name],
            table_name=entry_name,
            coltypes=coltypes,
            constraints=constraints,
            foreign_keys=foreign_keys,
        )

    def to_pushable_dataframes(
        self,
        coltypes: TableColumnDictionary[SQLType] = {},
        constraints: TableColumnDictionary[dict[str, Any]] = {},
        foreign_keys: TableColumnDictionary[ForeignKey] = {},
    ) -> list[PushableDF]:
        """Transform the current table state into a list of PushableDFs.

        Args:
            coltypes: a dictionary mapping table names to dictionaries mapping
                column names to their respective types.
            constraints: a dictionary mapping table names to dictionaries
                mapping column names to their desired constraints.
            foreign_keys: a dictionary mapping table names to dictionaries
                mapping column names to sqlalchemy ForeignKey objects.

        Returns:
            A list of PushableDFs with correctly annotated foreign keys and
                inferred column types.
        """
        all_foreign_keys = self.get_foreign_keys()

        return [
            self.__entry_to_pdf(
                table_name,
                coltypes.get(table_name, {}),
                constraints.get(table_name, {}),
                all_foreign_keys.get(table_name, {}) | foreign_keys.get(table_name, {}),
            )
            for table_name in self.__table_state.keys()
        ]
