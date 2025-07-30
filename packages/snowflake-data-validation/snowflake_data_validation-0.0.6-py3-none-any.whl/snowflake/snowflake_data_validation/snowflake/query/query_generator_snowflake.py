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

from typing import Union

from snowflake.snowflake_data_validation.configuration.model.table_configuration import (
    TableConfiguration,
)
from snowflake.snowflake_data_validation.connector.connector_base import ConnectorBase
from snowflake.snowflake_data_validation.query.query_generator_base import (
    QueryGeneratorBase,
)
from snowflake.snowflake_data_validation.snowflake.extractor.snowflake_cte_generator import (
    generate_cte_query,
    generate_outer_query,
)
from snowflake.snowflake_data_validation.utils.base_output_handler import (
    OutputHandlerBase,
)
from snowflake.snowflake_data_validation.utils.constants import (
    COL_NAME_NO_QUOTES_PLACEHOLDER,
    Platform,
)
from snowflake.snowflake_data_validation.utils.context import Context
from snowflake.snowflake_data_validation.utils.model.table_context import TableContext


LOGGER = logging.getLogger(__name__)


class QueryGeneratorSnowflake(QueryGeneratorBase):

    """Snowflake-specific implementation of query generator."""

    def generate_schema_query(self, table_context: TableContext) -> str:
        """Generate the SQL query to extract metadata for a specific table in Snowflake.

        This implementation will delegate to the existing template-based query generation
        or implement Snowflake-specific query logic.

        Args:
            table_context (TableContext): Configuration object containing table properties.

        Returns:
            str: SQL query string to extract metadata for the specified table.

        """
        query = table_context.sql_generator.generate_table_metadata_sql(
            platform=table_context.platform.value,
            table_name=table_context.table_name,
            schema_name=table_context.schema_name,
            fully_qualified_name=table_context.fully_qualified_name,
            where_clause=table_context.where_clause,
            has_where_clause=table_context.has_where_clause,
            column_selection_list=table_context.columns_to_validate,
        )

        return query

    def generate_metrics_query(
        self,
        table_context: TableContext,
        output_handler: OutputHandlerBase,
        connector: ConnectorBase,
    ) -> str:
        """Generate the SQL query to extract metadata for specific columns in a table in Snowflake.

        Args:
            table_context (TableConfiguration): Configuration object containing table properties.
            output_handler (OutputHandlerBase): Handler for output messages and progress reporting.
            connector (ConnectorBase): Database connector instance for executing queries.

        Returns:
            str: SQL query string to extract column metadata for the specified columns.

        """
        cte_queries = []
        cte_names = []
        metrics = []

        for col in table_context.columns_to_validate:
            col_name = col.name
            col_type = col.data_type

            # This is a temporary fix for current issue displaying "TEXT" instead of "VARCHAR" in the data_type column
            # TODO: Remove this once the issue is fixed
            if col_type == "TEXT":
                col_type = "VARCHAR"

            cte_query, cte_name, metric_list = generate_cte_query(
                metrics_templates=table_context.templates_loader_manager.metrics_templates,
                col_name=col_name,
                col_type=col_type,
                fully_qualified_name=table_context.fully_qualified_name,
                where_clause=table_context.where_clause,
                has_where_clause=table_context.has_where_clause,
                sql_generator=table_context.sql_generator,
            )
            if cte_query is None:
                continue
            cte_queries.append(cte_query)
            cte_names.append(cte_name)
            metrics.append(metric_list)

        if not cte_queries:
            error_message = (
                f"Metrics templates are missing for the column data types in "
                f"{table_context.fully_qualified_name}."
            )
            LOGGER.error(error_message)
            raise Exception(error_message)

        outer_query = generate_outer_query(cte_names, metrics)
        final_query = "WITH " + ", ".join(cte_queries) + "\n" + outer_query
        return final_query

    def generate_compute_md5_query(
        self, table_context: TableContext, other_table_name: str
    ) -> Union[str, list[str]]:

        chunk_id = table_context.get_chunk_id(other_table_name=other_table_name)

        datatypes_normalization_templates = (
            table_context.templates_loader_manager.datatypes_normalization_templates
        )
        datatypes_normalization_renderer_templates = {}
        for column in table_context.columns:
            normalization_template = datatypes_normalization_templates[column.data_type]
            normalization_template_rendered = normalization_template.replace(
                COL_NAME_NO_QUOTES_PLACEHOLDER, column.name
            )
            datatypes_normalization_renderer_templates[
                column.name
            ] = normalization_template_rendered

        queries = []

        chunk_row_concatenated_query = table_context.sql_generator.generate_chunk_row_concatenated_template_query(
            platform=table_context.platform.value,
            chunk_id=chunk_id,
            column_names_separate_by_comma=table_context.join_column_names_with_commas(),
            index_column_collection=table_context.index_column_collection,
            column_collection=table_context.columns_to_validate,
            datatypes_normalization_renderer_templates=datatypes_normalization_renderer_templates,
            fully_qualified_name=table_context.fully_qualified_name,
            has_where_clause=table_context.has_where_clause,
            where_clause=table_context.where_clause,
        )
        queries.append(chunk_row_concatenated_query)

        chunk_row_md5_query = (
            table_context.sql_generator.generate_chunk_row_md5_template_query(
                platform=table_context.platform.value,
                chunk_id=chunk_id,
                index_column_collection=table_context.index_column_collection,
            )
        )
        queries.append(chunk_row_md5_query)

        insert_chunk_row_md5_query = table_context.sql_generator.generate_insert_chunk_row_md5_template_query(
            platform=table_context.platform.value,
            normalized_fully_qualified_name=table_context.normalized_fully_qualified_name,
            chunk_id=chunk_id,
        )
        queries.append(insert_chunk_row_md5_query)

        return queries

    def generate_table_column_metadata_query(
        self, table_configuration: TableConfiguration, context: Context
    ) -> str:
        """Generate the SQL query to extract column information metadata for a given table in Snowflake.

        Args:
            table_configuration (TableConfiguration): Configuration object containing table properties.
            context (Context): The execution context containing relevant configuration and runtime information.

        Returns:
            str: SQL query string to extract column information metadata.

        """
        query = context.sql_generator.extract_table_column_metadata(
            database_name=table_configuration.source_database,
            schema_name=table_configuration.source_schema,
            table_name=table_configuration.source_table,
            platform=Platform.SNOWFLAKE.value,
        )

        return query

    def generate_statement_table_chunks_md5(self, table_context: TableContext) -> str:
        statement = table_context.sql_generator.generate_statement_table_chunks_md5(
            normalized_fully_qualified_name=table_context.normalized_fully_qualified_name,
            platform=table_context.platform.value,
        )

        return statement

    def generate_extract_chunks_md5_query(self, table_context: TableContext) -> str:
        query = table_context.sql_generator.generate_extract_chunks_md5_query(
            platform=table_context.platform.value,
            normalized_fully_qualified_name=table_context.normalized_fully_qualified_name,
        )

        return query

    def generate_extract_md5_rows_chunk_query(
        self, chunk_id: str, table_context: TableContext
    ) -> str:

        query = table_context.sql_generator.generate_extract_md5_rows_chunk_query(
            platform=table_context.platform.value,
            chunk_id=chunk_id,
            index_column_collection=table_context.index_column_collection,
        )

        return query
