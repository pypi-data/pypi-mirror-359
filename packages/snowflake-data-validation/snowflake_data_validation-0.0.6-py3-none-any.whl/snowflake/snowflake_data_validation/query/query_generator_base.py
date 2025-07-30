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

from abc import ABC, abstractmethod
from typing import Union

from snowflake.snowflake_data_validation.configuration.model.table_configuration import (
    TableConfiguration,
)
from snowflake.snowflake_data_validation.connector.connector_base import (
    ConnectorBase,
)
from snowflake.snowflake_data_validation.utils.context import Context
from snowflake.snowflake_data_validation.utils.model.table_context import TableContext


class QueryGeneratorBase(ABC):

    """Abstract base class for query generation.

    This class defines the interface for generating database queries that are
    used by both MetadataExtractorBase and ScriptWriterBase implementations.
    """

    @abstractmethod
    def generate_schema_query(self, table_context: TableContext) -> str:
        """Generate the SQL query to extract metadata for a specific table.

        Args:
            table_context (TableContext): Configuration object containing table properties.

        Returns:
            str: SQL query string to extract metadata for the specified table.

        """
        pass

    @abstractmethod
    def generate_metrics_query(
        self,
        table_context: TableContext,
        connector: ConnectorBase,
    ) -> str:
        """Generate the SQL query to extract metadata for specific columns in a table.

        Args:
            table_context (TableConfiguration): Configuration object containing table properties.
            metrics_templates (pd.DataFrame): DataFrame containing metrics templates to be applied.
            context (Context): The execution context containing relevant configuration and runtime information.
            connector (ConnectorBase): Database connector instance for executing queries.

        Returns:
            str: SQL query string to extract column metadata for the specified columns.

        """
        pass

    @abstractmethod
    def generate_statement_table_chunks_md5(self, table_context: TableContext) -> str:
        """Generate the DDL statement to create a table for storing MD5 checksums of data chunks.

        Args:
            table_context (TableContext): Configuration object containing table properties.

        Returns:
            str: SQL query string to create a table for storing MD5 checksums of data chunks.

        """
        pass

    @abstractmethod
    def generate_compute_md5_query(
        self, table_context: TableContext, other_table_name: str
    ) -> Union[str, list[str]]:
        """Generate the SQL query to compute MD5 for a table.

        Args:
            table_context (TableContext): Configuration object containing table properties.
            other_table_name (str): The name of the table to compute MD5 for.

        Returns:
            Union[str, list[str]]: SQL query string or a list of SQL query strings to extract MD5 checksum information.

        """
        pass

    @abstractmethod
    def generate_extract_chunks_md5_query(self, table_context: TableContext) -> str:
        """Generate the SQL query to extract MD5 for all chunks of a table.

        Args:
            table_context (TableContext): Configuration object containing table properties.

        Returns:
            str: SQL query string to extract MD5 for all chunks of a table.

        """
        pass

    @abstractmethod
    def generate_table_column_metadata_query(
        self, table_configuration: TableConfiguration, context: Context
    ) -> str:
        """Generate the SQL query to extract column information metadata for a given table.

        Args:
            table_configuration (TableConfiguration): Configuration object containing table properties.
            context (Context): The execution context containing relevant configuration and runtime information.

        Returns:
            str: SQL query string to extract column information metadata.

        """
        pass

    @abstractmethod
    def generate_extract_md5_rows_chunk_query(
        self, chunk_id: str, table_context: TableContext
    ) -> str:
        """Generate the SQL query to extract the MD5 rows for a specific chunk of a table.

        Args:
            chunk_id (str): The unique identifier for the chunk.
            table_context (TableContext): Configuration object containing table properties.

        Returns:
            str: SQL query string to extract the MD5 rows for the specified chunk.

        """
        pass
