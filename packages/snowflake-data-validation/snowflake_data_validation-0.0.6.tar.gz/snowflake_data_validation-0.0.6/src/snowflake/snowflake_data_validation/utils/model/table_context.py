# Copyright 2025 Snowflake Inc.
# SPDX-License-Identifier: Apache-2.0

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

# http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import re

from snowflake.snowflake_data_validation.extractor.sql_queries_template_generator import (
    SQLQueriesTemplateGenerator,
)
from snowflake.snowflake_data_validation.utils.constants import (
    CHUNK_ID_FORMAT,
    Origin,
    Platform,
)
from snowflake.snowflake_data_validation.utils.model.column_metadata import (
    ColumnMetadata,
)
from snowflake.snowflake_data_validation.utils.model.templates_loader_manager import (
    TemplatesLoaderManager,
)


class TableContext:

    """Context for a table in the data validation process.

    Attributes:
        platform (Platform): The platform where the table resides.
        origin (Origin): The origin of the table data.
        fully_qualified_name (str): The fully qualified name of the table.
        table_name (str): The name of the table.
        schema_name (str): The schema name of the table.
        database_name (str): The database name of the table.
        columns (list[ColumnMetadata]): List of column metadata for the table.
        run_id (str): Unique identifier for the validation run.
        run_start_time (str): Start time of the validation run.
        where_clause (str): The WHERE clause for filtering data.
        has_where_clause (bool): Indicates if a WHERE clause is present.
        use_as_exclude_list (bool): Indicates if the table is used as an exclude list
                                    for validation.
        column_selection_list (list[str]): List of columns to be selected for validation.
        templates_loader_manager (TemplatesLoaderManager): Manager for loading SQL templates.
        sql_generator (SQLQueriesTemplateGenerator): Generator for SQL queries.

    """

    def __init__(
        self,
        platform: Platform,
        origin: Origin,
        fully_qualified_name: str,
        table_name: str,
        schema_name: str,
        database_name: str,
        columns: list[ColumnMetadata],
        run_id: str,
        run_start_time: str,
        where_clause: str,
        has_where_clause: bool,
        use_as_exclude_list: bool,
        column_selection_list: list[str],
        templates_loader_manager: TemplatesLoaderManager,
        sql_generator: SQLQueriesTemplateGenerator,
        case_sensitive: bool = False,
    ):
        columns_to_validate = self.get_columns_to_validate(
            columns, column_selection_list, use_as_exclude_list
        )
        if not case_sensitive:
            # If case sensitivity is disabled, convert column names to uppercase
            columns_to_validate = [
                ColumnMetadata(
                    name=column.name.upper(),
                    data_type=column.data_type,
                    nullable=column.nullable,
                    is_primary_key=column.is_primary_key,
                    calculated_column_size_in_bytes=column.calculated_column_size_in_bytes,
                    properties=column.properties,
                )
                for column in columns_to_validate
            ]

        self.platform = platform
        self.origin = origin
        self.fully_qualified_name = fully_qualified_name
        self.database_name = database_name
        self.schema_name = schema_name
        self.table_name = table_name
        self.columns = columns
        self.where_clause = where_clause
        self.has_where_clause = has_where_clause
        self.use_as_exclude_list = use_as_exclude_list
        self.column_selection_list = [
            column.upper() for column in column_selection_list
        ]
        self.run_id = run_id
        self.run_start_time = run_start_time
        self.templates_loader_manager = templates_loader_manager
        self.sql_generator = sql_generator
        self.columns_to_validate = columns_to_validate
        self.case_sensitive = case_sensitive
        self.normalized_fully_qualified_name = (
            self._get_normalized_fully_qualified_name()
        )
        self.index_column_collection = self._get_index_column_collection()
        self.chunk_id_index = 0

    def get_columns_to_validate(
        self,
        full_table_column_list: list[ColumnMetadata],
        column_list: list[str],
        is_exclusion_mode: bool = False,
    ) -> list[ColumnMetadata]:
        """Return the list of columns to validate based on inclusion or exclusion mode.

        Args:
            full_table_column_list (list[str]): The complete list of columns in the table.
            column_list (list[str]): The list of columns to include or exclude.
            is_exclusion_mode (bool): If True, exclude the columns in column_list; otherwise, include them.

        Returns:
            list[str]: The list of columns to validate.

        """
        if (
            not column_list or len(column_list) == 0
        ):  # If no columns are specified, return all columns
            return full_table_column_list
        if not is_exclusion_mode:
            return [
                col
                for col in full_table_column_list
                if self._is_column_present(col.name, column_list)
            ]
        else:
            return [
                col
                for col in full_table_column_list
                if not self._is_column_present(col.name, column_list)
            ]

    def get_chunk_id(self, other_table_name: str) -> str:
        """Generate a unique chunk ID for the table context."""
        self.chunk_id_index = self.chunk_id_index + 1
        chunk_id = self.chunk_id_index

        chunk_id = ""
        if self.origin == Origin.SOURCE:
            chunk_id = CHUNK_ID_FORMAT.format(
                source_name=self.table_name,
                other_table_name=other_table_name,
                id=self.chunk_id_index,
            )
        else:
            chunk_id = CHUNK_ID_FORMAT.format(
                source_name=other_table_name,
                other_table_name=self.table_name,
                id=self.chunk_id_index,
            )

        return chunk_id

    def _is_column_present(self, column_name: str, column_list: list[str]) -> bool:
        """Check if a column exists in a list of columns.

        If the column list contains regular expressions,
        it checks if the column name matches any of the regular expressions.
        regular expressions are expected to start with 'r' and be wrapped between quotes e.g: r".*".

        Args:
            column_name (str): The name of the column to check.
            column_list (list[str]): The list of columns to search in.

        Returns:
            bool: True if the column exists in the list, False otherwise.

        """
        for col in column_list:
            if col.lower().startswith('r"') and col.endswith('"'):
                # If the column is a regex, check if it matches the column name
                regex_pattern = col[2:-1]  # Remove the 'r' and quotes
                if re.match(regex_pattern, column_name):
                    return True
            elif col == column_name:
                return True
        return False

    def _get_index_column_collection(self) -> list[str]:
        """Get a list of index columns for the table.

        Returns:
            list[str]: A list of index column names.

        """
        index_column_collection = [
            column for column in self.columns if column.is_primary_key
        ]

        return index_column_collection

    def _get_normalized_fully_qualified_name(self) -> str:
        """Normalize a fully qualified name by replacing dots and spaces with underscores.

        Returns:
            str: The normalized fully qualified name.

        """
        normalized_fully_qualified_name = self.fully_qualified_name.replace(
            ".", "_"
        ).replace(" ", "_")

        return normalized_fully_qualified_name

    def join_column_names_with_commas(self) -> str:
        """Join column names with commas and convert them to uppercase with quotes.

        Returns:
            str: A string of column names joined by commas, each in uppercase and quoted.

        """
        column_names_upper_and_quote = [
            f'"{col.name.upper()}"' for col in self.columns_to_validate
        ]
        return (
            ", ".join(column_names_upper_and_quote)
            if column_names_upper_and_quote
            else ""
        )
