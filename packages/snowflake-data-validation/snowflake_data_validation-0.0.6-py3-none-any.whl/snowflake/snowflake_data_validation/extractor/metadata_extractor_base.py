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

import logging

from abc import ABC, abstractmethod

import pandas as pd

from snowflake.snowflake_data_validation.configuration.model.table_configuration import (
    TableConfiguration,
)
from snowflake.snowflake_data_validation.connector.connector_base import (
    ConnectorBase,
)
from snowflake.snowflake_data_validation.query.query_generator_base import (
    QueryGeneratorBase,
)
from snowflake.snowflake_data_validation.utils.base_output_handler import (
    OutputHandlerBase,
)
from snowflake.snowflake_data_validation.utils.context import Context
from snowflake.snowflake_data_validation.utils.logging_utils import log
from snowflake.snowflake_data_validation.utils.model.table_context import TableContext


LOGGER = logging.getLogger(__name__)


class MetadataExtractorBase(ABC):

    """Provide interface for extracting metadata from various database sources.

    This class gets SQL queries from QueryGenerator and executes them to return DataFrames.
    """

    @log
    def __init__(
        self,
        connector: ConnectorBase,
        query_generator: QueryGeneratorBase,
        report_path: str = "",
    ):
        """Initialize the metadata extractor with a database connector and query generator.

        Args:
            connector: Database connector instance for the specific database type.
            query_generator: Query generator instance for generating SQL queries.
            report_path: Optional path for output reports.

        """
        LOGGER.debug("Initializing MetadataExtractorBase")
        self.connector = connector
        self.query_generator = query_generator
        self.report_path = report_path
        self.columns_metrics = {}
        LOGGER.debug(
            "MetadataExtractorBase initialized with connector and query generator"
        )

    @abstractmethod
    def extract_schema_metadata(
        self,
        table_context: TableContext,
        output_handler: OutputHandlerBase,
    ) -> pd.DataFrame:
        """Extract table-level metadata for the specified table.

        Args:
            table_context (TableContext): Configuration object containing table properties.
            output_handler (OutputHandlerBase): Output handler for logging and reporting.

        Returns:
            pd.DataFrame: A DataFrame containing table metadata including row count, column count, etc.

        """
        pass

    @abstractmethod
    def extract_metrics_metadata(
        self,
        table_context: TableContext,
        output_handler: OutputHandlerBase,
    ) -> pd.DataFrame:
        """Extract column-level metadata for the specified columns in a table.

        Args:
            table_context (TableContext): Configuration object containing table properties and columns.
            output_handler (OutputHandlerBase): Output handler for logging and reporting.

        Returns:
            pd.DataFrame: A DataFrame containing column metadata including:
                          - data types
                          - nullability
                          - descriptive statistics (min, max, avg, etc.)
                          - distinct values count
                          - other column-specific attributes

        Raises:
            ValueError: If the table or specified columns don't exist.

        """
        pass

    @abstractmethod
    def extract_table_column_metadata(
        self, table_configuration: TableConfiguration, context: Context
    ) -> pd.DataFrame:
        """Extract column information metadata for a given table.

        Args:
            table_configuration (TableConfiguration): The table configuration containing all necessary metadata.
            context (Context): The execution context containing relevant configuration and runtime information.

        Returns:
            pd.DataFrame: A DataFrame containing column information metadata.

        """
        pass

    @abstractmethod
    def create_table_chunks_md5(self, table_context: TableContext) -> None:
        """Create table chunks for MD5 calculation.

        Args:
            table_context (TableContext): Configuration object containing table properties.

        """
        pass

    @abstractmethod
    def compute_md5(self, table_context: TableContext, other_table_name: str) -> None:
        """Compute MD5 for a specified table.

        Args:
            table_context (TableContext): Configuration object containing table properties.
            other_table_name (str): the name of the equivalent table in other platform.

        Raises:
            ValueError: If the table or specified columns don't exist.
            DatabaseError: If there is an error executing the SQL query.

        """
        pass

    @abstractmethod
    def extract_chunks_md5(
        self,
        table_context: TableContext,
    ) -> pd.DataFrame:
        """Extract MD5 for all chunks of a specified table.

        Args:
            table_context (TableContext): Configuration object containing table properties.

        Returns:
            pd.DataFrame: A DataFrame containing the MD5 checksums for each chunk of the specified table.

        """
        pass

    @abstractmethod
    def extract_md5_rows_chunk(
        self, chunk_id: str, table_context: TableContext
    ) -> pd.DataFrame:
        """Extract MD5 rows for a specific chunk of a table.

        Args:
            chunk_id (str): The ID of the chunk for which to extract the MD5.
            table_context (TableContext): table column metadata containing column definitions and types.

        Returns:
            pd.DataFrame: A DataFrame containing the MD5 rows for the specified chunk.

        """
        pass
