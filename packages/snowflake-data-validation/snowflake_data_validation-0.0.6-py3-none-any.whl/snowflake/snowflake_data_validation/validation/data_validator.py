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
import os
import re

import pandas as pd

from snowflake.snowflake_data_validation.utils.base_output_handler import (
    OutputMessageLevel,
)
from snowflake.snowflake_data_validation.utils.constants import (
    CHUNK_ID_COLUMN_KEY,
    CHUNK_MD5_VALUE_COLUMN_KEY,
    COLUMN_DATATYPE,
    COLUMN_VALIDATED,
    MD5_REPORT_QUERY_TEMPLATE,
    NEWLINE,
    NOT_APPLICABLE_CRITERIA_VALUE,
    NOT_EXIST_TARGET,
    RESULT_COLUMN_KEY,
    ROW_NUMBER_COLUMN_KEY,
    SOURCE_QUERY_COLUMN_KEY,
    TABLE_NAME_COLUMN_KEY,
    TABLE_NAME_KEY,
    TARGET_QUERY_COLUMN_KEY,
    UNDERSCORE_MERGE_COLUMN_KEY,
    ValidationLevel,
)
from snowflake.snowflake_data_validation.utils.context import Context
from snowflake.snowflake_data_validation.utils.logging_utils import log
from snowflake.snowflake_data_validation.validation.validation_report_buffer import (
    ValidationReportBuffer,
)


LOGGER = logging.getLogger(__name__)
IS_NUMERIC_REGEX = r"^-?\d+(\.\d+)?$"
VALIDATION_REPORT_NAME = "data_validation_report.csv"
ROW_VALIDATION_REPORT_NAME = "{fully_qualified_name}_row_validation_report.csv"
ROW_VALIDATION_DIFF_QUERY_NAME = (
    "{fully_qualified_name}_{platform}_row_validation_diff_query.sql"
)


def _normalize_datatype(datatype: str) -> str:
    """Normalize data types to handle equivalent types.

    This is a temporary fix for the issue where Snowflake displays "TEXT" instead of "VARCHAR".
    TODO: Remove this once the issue is fixed.

    Args:
        datatype (str): The data type to normalize.

    Returns:
        str: The normalized data type.

    """
    # Treat VARCHAR and TEXT as equivalent
    if datatype.upper() in {"VARCHAR", "TEXT"}:
        return "VARCHAR"
    return datatype.upper()


def _create_validation_row(
    validation_type: str,
    table_name: str,
    column_validated: str,
    evaluation_criteria: str,
    source_value: any,
    snowflake_value: any,
    status: str,
    comments: str,
) -> pd.DataFrame:
    """Create a standardized validation result row.

    Args:
        validation_type (str): The type of validation being performed.
        table_name (str): The name of the table being validated.
        column_validated (str): The column being validated.
        evaluation_criteria (str): The criteria used for evaluation.
        source_value (any): The value from the source.
        snowflake_value (any): The value from Snowflake.
        status (str): The validation status (SUCCESS/FAILURE).
        comments (str): Additional comments about the validation.

    Returns:
        pd.DataFrame: A single-row DataFrame with the validation result.

    """
    return pd.DataFrame(
        {
            "VALIDATION_TYPE": [validation_type],
            "TABLE": [table_name],
            "COLUMN_VALIDATED": [column_validated],
            "EVALUATION_CRITERIA": [evaluation_criteria],
            "SOURCE_VALUE": [source_value],
            "SNOWFLAKE_VALUE": [snowflake_value],
            "STATUS": [status],
            "COMMENTS": [comments],
        }
    )


def _add_validation_row_to_data(
    differences_data: pd.DataFrame, validation_row: pd.DataFrame
) -> pd.DataFrame:
    """Add a validation row to the differences data."""
    return pd.concat([differences_data, validation_row], ignore_index=True)


def _validate_datatype_field(
    source_value: str,
    target_value: str,
    context: Context,
    object_name: str,
    source_validated_value: str,
    column: str,
) -> tuple[pd.DataFrame, bool]:
    """Validate datatype field with mapping logic.

    Returns:
        tuple: (validation_row_df, is_success)

    """
    if context.datatypes_mappings:
        mapped_value = context.datatypes_mappings.get(source_value.upper(), None)
        if mapped_value and _normalize_datatype(target_value) == _normalize_datatype(
            mapped_value
        ):
            success_message = (
                f"Values match: source({source_value}) "
                f"has a mapping to Snowflake({target_value})"
            )
            return (
                _create_validation_row(
                    validation_type=ValidationLevel.SCHEMA_VALIDATION.value,
                    table_name=object_name,
                    column_validated=source_validated_value,
                    evaluation_criteria=column,
                    source_value=source_value,
                    snowflake_value=target_value,
                    status="SUCCESS",
                    comments=success_message,
                ),
                True,
            )
        else:
            comment = (
                f"No mapping found for datatype '{source_value}': "
                f"source({source_value}), Snowflake({target_value})"
                if not mapped_value
                else f"Values differ: source({source_value}), Snowflake({target_value})"
            )
            LOGGER.debug(
                "Datatype mismatch for column %s: source=%s, target=%s",
                source_validated_value,
                source_value,
                target_value,
            )
            return (
                _create_validation_row(
                    validation_type=ValidationLevel.SCHEMA_VALIDATION.value,
                    table_name=object_name,
                    column_validated=source_validated_value,
                    evaluation_criteria=column,
                    source_value=source_value,
                    snowflake_value=target_value,
                    status="FAILURE",
                    comments=comment,
                ),
                False,
            )
    else:
        # No mappings available - direct comparison
        if source_value.upper() == target_value.upper():
            return (
                _create_validation_row(
                    validation_type=ValidationLevel.SCHEMA_VALIDATION.value,
                    table_name=object_name,
                    column_validated=source_validated_value,
                    evaluation_criteria=column,
                    source_value=source_value,
                    snowflake_value=target_value,
                    status="SUCCESS",
                    comments=f"Values match: source({source_value}), Snowflake({target_value})",
                ),
                True,
            )
        else:
            LOGGER.debug(
                "Datatype mismatch for column %s: source=%s, target=%s",
                source_validated_value,
                source_value,
                target_value,
            )
            return (
                _create_validation_row(
                    validation_type=ValidationLevel.SCHEMA_VALIDATION.value,
                    table_name=object_name,
                    column_validated=source_validated_value,
                    evaluation_criteria=column,
                    source_value=source_value,
                    snowflake_value=target_value,
                    status="FAILURE",
                    comments=f"Values differ: source({source_value}), Snowflake({target_value})",
                ),
                False,
            )


def _validate_column_field(
    column: str,
    source_value: any,
    target_value: any,
    context: Context,
    object_name: str,
    source_validated_value: str,
) -> tuple[pd.DataFrame, bool]:
    """Validate a single column field and return validation row and success status.

    Returns:
        tuple: (validation_row_df, is_success)

    """
    # Skip if both values are NaN or identical
    if pd.isna(source_value) and pd.isna(target_value):
        return pd.DataFrame(), True  # No validation row needed, but success

    if source_value == target_value:
        return (
            _create_validation_row(
                validation_type=ValidationLevel.SCHEMA_VALIDATION.value,
                table_name=object_name,
                column_validated=source_validated_value,
                evaluation_criteria=column,
                source_value=source_value,
                snowflake_value=target_value,
                status="SUCCESS",
                comments=f"Values match: source({source_value}), Snowflake({target_value})",
            ),
            True,
        )

    # Handle datatype validation with special logic
    if column == COLUMN_DATATYPE:
        return _validate_datatype_field(
            source_value,
            target_value,
            context,
            object_name,
            source_validated_value,
            column,
        )

    # Handle specific precision/scale/length criteria with WARNING status
    warning_criteria = {
        "NUMERIC_PRECISION",
        "NUMERIC_SCALE",
        "CHARACTER_MAXIMUM_LENGTH",
    }
    if column in warning_criteria:

        if is_numeric(source_value) and is_numeric(target_value):
            if float(source_value) < float(target_value):
                return (
                    _create_validation_row(
                        validation_type=ValidationLevel.SCHEMA_VALIDATION.value,
                        table_name=object_name,
                        column_validated=source_validated_value,
                        evaluation_criteria=column,
                        source_value=source_value,
                        snowflake_value=target_value,
                        status="WARNING",
                        comments=f"Source value ({source_value}) is lower than target value ({target_value})",
                    ),
                    True,  # Consider WARNING as success
                )

    # Handle FAILURE status
    LOGGER.debug(
        "Value mismatch for column %s in %s: source=%s, target=%s",
        source_validated_value,
        column,
        source_value,
        target_value,
    )
    return (
        _create_validation_row(
            validation_type=ValidationLevel.SCHEMA_VALIDATION.value,
            table_name=object_name,
            column_validated=source_validated_value,
            evaluation_criteria=column,
            source_value=source_value,
            snowflake_value=target_value,
            status="FAILURE",
            comments=f"Values differ: source({source_value}), Snowflake({target_value})",
        ),
        False,
    )


@log
def validate_table_metadata(
    object_name: str, target_df: pd.DataFrame, source_df: pd.DataFrame, context: Context
) -> bool:
    """Validate the metadata of two tables by normalizing and comparing their dataframes.

    Args:
        object_name (str): The name of the object (e.g., table) being validated.
        target_df (pd.DataFrame): The dataframe representing the target table's metadata.
        source_df (pd.DataFrame): The dataframe representing the source table's metadata.
        context (Context): The execution context containing relevant configuration and runtime information.

    Returns:
        bool: True if the normalized dataframes are equal, False otherwise.

    """
    LOGGER.info("Starting table metadata validation for: %s", object_name)
    context.output_handler.handle_message(
        message=f"Running Schema Validation for {object_name}",
        level=OutputMessageLevel.INFO,
    )

    LOGGER.debug("Normalizing target and source DataFrames")
    normalized_target = normalize_dataframe(target_df)
    normalized_source = normalize_dataframe(source_df)

    differences_data = pd.DataFrame(
        columns=[
            "VALIDATION_TYPE",
            "TABLE",
            "COLUMN_VALIDATED",
            "EVALUATION_CRITERIA",
            "SOURCE_VALUE",
            "SNOWFLAKE_VALUE",
            "STATUS",
            "COMMENTS",
        ]
    )

    target_validated_set = set(normalized_target[COLUMN_VALIDATED].values)

    for _, source_row in normalized_source.iterrows():
        source_validated_value = source_row[COLUMN_VALIDATED]

        # Handle missing columns in target
        if source_validated_value not in target_validated_set:
            LOGGER.debug("Column %s not found in target table", source_validated_value)
            new_row = _create_validation_row(
                validation_type=ValidationLevel.SCHEMA_VALIDATION.value,
                table_name=object_name,
                column_validated=source_validated_value,
                evaluation_criteria=COLUMN_VALIDATED,
                source_value=source_validated_value,
                snowflake_value=NOT_EXIST_TARGET,
                status="FAILURE",
                comments="The column does not exist in the target table.",
            )
            differences_data = _add_validation_row_to_data(differences_data, new_row)
            continue

        # Validate existing columns
        target_row = normalized_target[
            normalized_target[COLUMN_VALIDATED] == source_validated_value
        ]
        column_has_differences = False

        for column in normalized_source.columns:
            # Skip irrelevant columns
            if column in {COLUMN_VALIDATED, TABLE_NAME_KEY}:
                continue

            source_value = source_row[column]
            target_value = target_row[column].values[0]

            validation_row, field_success = _validate_column_field(
                column,
                source_value,
                target_value,
                context,
                object_name,
                source_validated_value,
            )

            if not validation_row.empty:
                differences_data = _add_validation_row_to_data(
                    differences_data, validation_row
                )

            if not field_success:
                column_has_differences = True

        # Record overall column success if no field differences found
        if not column_has_differences:
            success_row = _create_validation_row(
                validation_type=ValidationLevel.SCHEMA_VALIDATION.value,
                table_name=object_name,
                column_validated=source_validated_value,
                evaluation_criteria=COLUMN_VALIDATED,
                source_value=source_validated_value,
                snowflake_value=source_validated_value,
                status="SUCCESS",
                comments="Column exists in target table and all metadata matches.",
            )
            differences_data = _add_validation_row_to_data(
                differences_data, success_row
            )

    # Filter out rows where both SOURCE and TARGET are NOT_APPLICABLE_CRITERIA_VALUE
    # These represent validation criteria that don't apply to certain data types
    differences_data = differences_data[
        ~(
            (differences_data["SOURCE_VALUE"] == NOT_APPLICABLE_CRITERIA_VALUE)
            & (differences_data["SNOWFLAKE_VALUE"] == NOT_APPLICABLE_CRITERIA_VALUE)
        )
    ]

    # Determine if there are actual failures (excluding WARNING status)
    failure_rows = differences_data[differences_data["STATUS"] == "FAILURE"]
    has_failures = len(failure_rows) > 0

    buffer = ValidationReportBuffer()
    buffer.add_data(differences_data)
    LOGGER.debug(
        "Added schema validation data for %s to buffer (queue size: %d)",
        object_name,
        buffer.get_queue_size(),
    )

    display_data = differences_data.drop(
        columns=["VALIDATION_TYPE", "TABLE"], errors="ignore"
    )

    context.output_handler.handle_message(
        header="Schema validation results:",
        dataframe=display_data,
        level=(OutputMessageLevel.WARNING if has_failures else OutputMessageLevel.INFO),
    )

    return not has_failures


@log
def validate_column_metadata(
    object_name: str,
    target_df: pd.DataFrame,
    source_df: pd.DataFrame,
    context: Context,
    tolerance: float = 0.001,
) -> bool:
    """Validate that the column metadata of the target DataFrame matches the source DataFrame.

    This method normalizes both the target and source DataFrames and then compares their
    column metadata cell by cell to ensure they are equivalent within a given tolerance.

    Args:
        object_name (str): The name of the object (e.g., table) being validated.
        target_df (pd.DataFrame): The target DataFrame whose column metadata is to be validated.
        source_df (pd.DataFrame): The source DataFrame to compare against.
        context (Context): The execution context containing relevant configuration and runtime information.
        tolerance (float, optional): The tolerance level for numerical differences. Defaults to 0.001.

    Returns:
        bool: True if the column metadata of both DataFrames are equal within the tolerance, False otherwise.

    """
    LOGGER.info(
        "Starting column metadata validation for: %s with tolerance: %f",
        object_name,
        tolerance,
    )
    context.output_handler.handle_message(
        message=f"Running Metrics Validation for {object_name}",
        level=OutputMessageLevel.INFO,
    )

    normalized_target = normalize_dataframe(target_df)
    normalized_source = normalize_dataframe(source_df)

    differences_data = pd.DataFrame(
        columns=[
            "VALIDATION_TYPE",
            "TABLE",
            "COLUMN_VALIDATED",
            "EVALUATION_CRITERIA",
            "SOURCE_VALUE",
            "SNOWFLAKE_VALUE",
            "STATUS",
            "COMMENTS",
        ]
    )
    target_validated_set = set(normalized_target[COLUMN_VALIDATED].values)

    has_differences = False

    for _, source_row in normalized_source.iterrows():
        column_name = source_row[COLUMN_VALIDATED]
        source_validated_value = source_row[COLUMN_VALIDATED]

        if source_validated_value not in target_validated_set:
            new_row = _create_validation_row(
                validation_type=ValidationLevel.METRICS_VALIDATION.value,
                table_name=object_name,
                column_validated=source_validated_value,
                evaluation_criteria=COLUMN_VALIDATED,
                source_value=source_validated_value,
                snowflake_value=NOT_EXIST_TARGET,
                status="FAILURE",
                comments="The column does not exist in the target table.",
            )
            differences_data = pd.concat([differences_data, new_row], ignore_index=True)
            has_differences = True
        else:
            target_row = normalized_target[
                normalized_target[COLUMN_VALIDATED] == source_validated_value
            ]

            column_has_differences = False

            for col in normalized_source.columns:
                if col == COLUMN_VALIDATED or col == TABLE_NAME_KEY:
                    continue

                source_value = source_row[col]
                target_value = target_row[col].values[0]

                # Skip if both values are NaN or identical
                if pd.isna(source_value) and pd.isna(target_value):
                    # Record successful validation for NaN values
                    success_row = _create_validation_row(
                        validation_type=ValidationLevel.METRICS_VALIDATION.value,
                        table_name=object_name,
                        column_validated=column_name,
                        evaluation_criteria=col,
                        source_value="NULL",
                        snowflake_value="NULL",
                        status="SUCCESS",
                        comments="Both values are NULL/NaN - validation passed",
                    )
                    differences_data = pd.concat(
                        [differences_data, success_row], ignore_index=True
                    )
                    continue
                if source_value == target_value:
                    # Record successful validation for exact matches
                    success_row = _create_validation_row(
                        validation_type=ValidationLevel.METRICS_VALIDATION.value,
                        table_name=object_name,
                        column_validated=column_name,
                        evaluation_criteria=col,
                        source_value=str(source_value),
                        snowflake_value=str(target_value),
                        status="SUCCESS",
                        comments=f"Values match exactly: {source_value}",
                    )
                    differences_data = pd.concat(
                        [differences_data, success_row], ignore_index=True
                    )
                    continue

                # Check numeric values with tolerance
                if is_numeric(source_value) and is_numeric(target_value):
                    source_num = float(source_value)
                    target_num = float(target_value)
                    if abs(source_num - target_num) <= tolerance:
                        # Record successful validation within tolerance
                        success_row = _create_validation_row(
                            validation_type=ValidationLevel.METRICS_VALIDATION.value,
                            table_name=object_name,
                            column_validated=column_name,
                            evaluation_criteria=col,
                            source_value=str(source_value),
                            snowflake_value=str(target_value),
                            status="SUCCESS",
                            comments=(
                                f"Values within tolerance ({tolerance}): "
                                f"source({source_value}), target({target_value})"
                            ),
                        )
                        differences_data = pd.concat(
                            [differences_data, success_row], ignore_index=True
                        )
                        continue
                    comment = (
                        f"Values differ beyond tolerance of {tolerance}: "
                        f"source({source_value}), target({target_value})"
                    )
                else:
                    comment = (
                        f"Values differ: source({source_value}), target({target_value})"
                    )

                column_has_differences = True
                has_differences = True
                new_row = _create_validation_row(
                    validation_type=ValidationLevel.METRICS_VALIDATION.value,
                    table_name=object_name,
                    column_validated=column_name,
                    evaluation_criteria=col,
                    source_value=str(source_value),
                    snowflake_value=str(target_value),
                    status="FAILURE",
                    comments=comment,
                )
                differences_data = pd.concat(
                    [differences_data, new_row], ignore_index=True
                )

            # If the column exists and had no differences, record overall column success
            if not column_has_differences:
                success_row = _create_validation_row(
                    validation_type=ValidationLevel.METRICS_VALIDATION.value,
                    table_name=object_name,
                    column_validated=column_name,
                    evaluation_criteria=COLUMN_VALIDATED,
                    source_value=source_validated_value,
                    snowflake_value=source_validated_value,
                    status="SUCCESS",
                    comments="Column exists in target table and all metrics match.",
                )
                differences_data = pd.concat(
                    [differences_data, success_row], ignore_index=True
                )

    # Add validation data to buffer instead of writing directly to file
    buffer = ValidationReportBuffer()

    # Filter out rows where both SOURCE and TARGET are NOT_APPLICABLE_CRITERIA_VALUE
    # These represent validation criteria that don't apply to certain data types
    differences_data = differences_data[
        ~(
            (differences_data["SOURCE_VALUE"] == NOT_APPLICABLE_CRITERIA_VALUE)
            & (differences_data["SNOWFLAKE_VALUE"] == NOT_APPLICABLE_CRITERIA_VALUE)
        )
    ]

    buffer.add_data(differences_data)
    LOGGER.debug(
        "Added metrics validation data for %s to buffer (queue size: %d)",
        object_name,
        buffer.get_queue_size(),
    )

    display_data = differences_data.drop(
        columns=["VALIDATION_TYPE", "TABLE"], errors="ignore"
    )

    context.output_handler.handle_message(
        header="Metrics validation results:",
        dataframe=display_data,
        level=(
            OutputMessageLevel.WARNING if has_differences else OutputMessageLevel.INFO
        ),
    )

    return not has_differences


@log
def validate_non_numeric_difference(
    differences_data, object_name, column_name, metric, source_value, target_value
):
    """Validate non-numeric differences between source and target values for a specific column and metric.

    This function checks if there is a difference between the source and target values for a given column and metric.
    If a difference is found, it creates a new metadata row describing the discrepancy and appends it to the
    `differences_data` DataFrame.

    Args:
        differences_data (pd.DataFrame): A DataFrame containing metadata about differences identified during validation.
        object_name (str): The name of the object (e.g., table) being validated.
        column_name (str): The name of the column being validated.
        metric (str): The metric or validation rule being applied.
        source_value (Any): The value from the source dataset.
        target_value (Any): The value from the target dataset.

    Returns:
        pd.DataFrame: An updated DataFrame with the original differences and a new row if a difference was found.

    """
    LOGGER.debug(
        "Validating non-numeric difference for %s.%s.%s: source=%s, target=%s",
        object_name,
        column_name,
        metric,
        source_value,
        target_value,
    )
    new_row = _create_validation_row(
        validation_type=ValidationLevel.METRICS_VALIDATION.value,
        table_name=object_name,
        column_validated=column_name,
        evaluation_criteria=metric,
        source_value=source_value,
        snowflake_value=target_value,
        status="FAILURE",
        comments=f"Values differ: source({source_value}), target({target_value}).",
    )
    if not new_row.empty:
        differences_data = (
            pd.concat([differences_data, new_row], ignore_index=True)
            if not differences_data.empty
            else new_row
        )

    return differences_data


@log
def validate_numeric_difference(
    tolerance: float,
    differences_data: pd.DataFrame,
    object_name: str,
    column_name: str,
    metric: str,
    source_value: any,
    target_value: any,
    context: Context,
):
    """Validate the numeric difference between source and target values against a specified tolerance.

    This function checks if the absolute difference between the source and target values exceeds the given tolerance.
    If the difference is greater than the tolerance, it creates a new metadata row describing the discrepancy and
    appends it to the `differences_data` DataFrame.

    Args:
        tolerance (float): The maximum allowable difference between the source and target values.
        differences_data (pd.DataFrame): A DataFrame containing metadata about detected differences.
        object_name (str): The name of the object (e.g., table) being validated.
        column_name (str): The name of the column being validated.
        metric (str): The metric or description associated with the validation.
        source_value (float or str): The source value to be compared.
        target_value (float or str): The target value to be compared.
        context (Context): The execution context containing relevant configuration and runtime information.

    Returns:
        tuple: A tuple containing:
            - differences_data (pd.DataFrame): The updated DataFrame with any new discrepancy metadata rows appended.
            - source_value (float): The source value converted to a float.
            - target_value (float): The target value converted to a float.

    Raises:
        ValueError: If the source or target values cannot be converted to floats.

    Notes:
        - If the `differences_data` DataFrame is empty, it initializes it with the new metadata row.

    """
    LOGGER.debug(
        "Validating numeric difference for %s.%s.%s with tolerance %f: source=%s, target=%s",
        object_name,
        column_name,
        metric,
        tolerance,
        source_value,
        target_value,
    )
    # WIP: This is a temporary solution to handle the case when the value is a string representation of a number.
    target_value = float(target_value)
    source_value = float(source_value)
    if abs(target_value - source_value) > tolerance:
        new_row = _create_validation_row(
            validation_type=ValidationLevel.METRICS_VALIDATION.value,
            table_name=object_name,
            column_validated=column_name,
            evaluation_criteria=metric,
            source_value=source_value,
            snowflake_value=target_value,
            status="FAILURE",
            comments=f"Values differ ({source_value} != {target_value}) beyond tolerance.",
        )
        if not new_row.empty:
            differences_data = (
                pd.concat([differences_data, new_row], ignore_index=True)
                if not differences_data.empty
                else new_row
            )
    else:
        context.output_handler.handle_message(
            header="Disregarding numeric difference.",
            message=(
                f"Source value: {source_value} and Target value: {target_value} "
                f"do not differ beyond tolerance. {tolerance}"
            ),
            level=OutputMessageLevel.WARNING,
        )
    return differences_data, source_value, target_value


def normalize_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize the DataFrame by standardizing column names and types.

    Args:
        df (pd.DataFrame): The DataFrame to normalize.

    Returns:
        pd.DataFrame: A normalized DataFrame with uppercase column names, NaN values filled with
                     NOT_APPLICABLE_CRITERIA_VALUE, and rows sorted by all columns.

    """
    df.columns = [
        col.upper() for col in df.columns
    ]  # WIP in the future we should generate the columns names from a column mapping if provided
    df_copy = df.fillna(NOT_APPLICABLE_CRITERIA_VALUE, inplace=False)
    return df_copy.sort_values(by=list(df_copy.columns)).reset_index(drop=True)


def is_numeric(value: any) -> bool:
    """Determine if the given value is numeric.

    A value is considered numeric if it is an instance of int or float,
    or if it matches the numeric pattern (including integers and decimals).
    As a safety net, if the regex check passes, we also verify that the
    value can actually be converted to float.

    Args:
        value: The value to check. Can be of any type.

    Returns:
        bool: True if the value is numeric, False otherwise.

    """
    if isinstance(value, (int, float)):
        return True

    if bool(re.match(IS_NUMERIC_REGEX, str(value))):
        try:
            float(value)
            return True
        except (ValueError, TypeError):
            return False

    return False


def get_diff_md5_chunks(
    source_md5_checksum_df: pd.DataFrame,
    target_md5_checksum_df: pd.DataFrame,
) -> pd.DataFrame:
    """Get the differences in MD5 checksums between source and target DataFrames.

    This function compares the MD5 checksums of two DataFrames and returns a DataFrame containing
    the differences found, including chunk IDs and MD5 value.

    Args:
        source_md5_checksum_df (pd.DataFrame): The source DataFrame containing MD5 checksums.
        target_md5_checksum_df (pd.DataFrame): The target DataFrame containing MD5 checksums.

    Returns:
        pd.DataFrame: A DataFrame containing the differences in MD5 checksums.

    """
    source_intersection_target = pd.merge(
        source_md5_checksum_df,
        target_md5_checksum_df,
        on=[CHUNK_ID_COLUMN_KEY, CHUNK_MD5_VALUE_COLUMN_KEY],
        how="inner",
    )

    source_except_intersection = source_md5_checksum_df[
        ~source_md5_checksum_df[CHUNK_ID_COLUMN_KEY].isin(
            source_intersection_target[CHUNK_ID_COLUMN_KEY]
        )
    ]
    target_except_intersection = target_md5_checksum_df[
        ~target_md5_checksum_df[CHUNK_ID_COLUMN_KEY].isin(
            source_intersection_target[CHUNK_ID_COLUMN_KEY]
        )
    ]

    diff_df = pd.merge(
        source_except_intersection,
        target_except_intersection,
        on=[CHUNK_ID_COLUMN_KEY],
        how="left",
        suffixes=("_SOURCE", "_TARGET"),
    )

    return diff_df


def get_diff_md5_rows_chunk(
    source_md5_rows_chunk: pd.DataFrame,
    target_md5_rows_chunk: pd.DataFrame,
    source_index_column_collection: list[str],
    target_index_column_collection: list[str],
) -> pd.DataFrame:
    """Get the differences in MD5 for a specific chunk row.

    Args:
        source_md5_rows_chunk (pd.DataFrame): The source DataFrame
        containing MD5 for a specific chunk row.
        target_md5_rows_chunk (pd.DataFrame): The target DataFrame
        containing MD5 for a specific chunk row.
        source_index_column_collection (list[str]): A list of index columns for the source DataFrame.
        target_index_column_collection (list[str]): A list of index columns for the target DataFrame.

    Returns:
        pd.DataFrame: A DataFrame containing the differences in MD5 for the specified chunk row.

    """
    source_merge_target = pd.merge(
        source_md5_rows_chunk,
        target_md5_rows_chunk,
        left_on=source_index_column_collection,
        right_on=target_index_column_collection,
        how="outer",
        suffixes=("_SOURCE", "_TARGET"),
        indicator=True,
    )

    not_found_df = source_merge_target[
        source_merge_target[UNDERSCORE_MERGE_COLUMN_KEY] != "both"
    ]
    not_found_df_copy = not_found_df.copy()
    not_found_df_copy[RESULT_COLUMN_KEY] = "NOT_FOUND"

    failed_df = source_merge_target[
        (source_merge_target[UNDERSCORE_MERGE_COLUMN_KEY] == "both")
        & (
            source_merge_target["ROW_MD5_SOURCE"]
            != source_merge_target["ROW_MD5_TARGET"]
        )
    ]
    failed_df_copy = failed_df.copy()
    failed_df_copy[RESULT_COLUMN_KEY] = "FAILED"

    columns = source_index_column_collection + [RESULT_COLUMN_KEY]
    diff_df = pd.concat([not_found_df_copy, failed_df_copy], ignore_index=True)[columns]
    diff_df_ordered = diff_df.sort_values(by=source_index_column_collection)
    return diff_df_ordered


def generate_row_validation_report(
    compared_df: pd.DataFrame,
    fully_qualified_name: str,
    target_fully_qualified_name: str,
    source_index_column_collection: list[str],
    target_index_column_collection: list[str],
    context: Context,
) -> pd.DataFrame:
    """Store a report for MD5 rows chunk validation.

    Args:
        compared_df (pd.DataFrame): The DataFrame containing the compared MD5 checksums.
        fully_qualified_name (str): The fully qualified name of the table being validated.
        target_fully_qualified_name (str): The fully qualified name of the target table being validated.
        source_index_column_collection (list[str]): A list of index columns for the source DataFrame.
        target_index_column_collection (list[str]): A list of index columns for the target DataFrame
        context (Context): The execution context containing relevant configuration and runtime information.

    Returns:
        pd.DataFrame: A DataFrame containing the validation results, including row numbers, table names

    """
    result_columns = (
        [ROW_NUMBER_COLUMN_KEY, TABLE_NAME_COLUMN_KEY]
        + source_index_column_collection
        + [
            RESULT_COLUMN_KEY,
            SOURCE_QUERY_COLUMN_KEY,
            TARGET_QUERY_COLUMN_KEY,
        ]
    )

    result_df = pd.DataFrame(data=[], columns=result_columns)
    for _, row in compared_df.iterrows():
        values = []
        row_number = context.get_row_number()
        values.append(row_number)
        values.append(fully_qualified_name)

        for index_column in source_index_column_collection:
            values.append(row[index_column])

        values.append(row[RESULT_COLUMN_KEY])

        source_query = _generate_select_all_columns_query(
            fully_qualified_name=fully_qualified_name,
            index_column_collection=source_index_column_collection,
            df_row=row,
        )

        values.append(source_query)

        target_query = _generate_select_all_columns_query(
            fully_qualified_name=target_fully_qualified_name,
            index_column_collection=target_index_column_collection,
            df_row=row,
        )

        values.append(target_query)

        result_df.loc[len(result_df)] = values

    report_name = ROW_VALIDATION_REPORT_NAME.format(
        fully_qualified_name=fully_qualified_name
    )
    report_file = os.path.join(
        context.report_path, f"{context.run_start_time}_{report_name}"
    )

    result_df.to_csv(report_file, index=False)


def generate_row_validation_queries(
    compared_df: pd.DataFrame,
    fully_qualified_name: str,
    target_fully_qualified_name: str,
    source_index_column_collection: list[str],
    target_index_column_collection: list[str],
    context: Context,
) -> None:
    """Generate SQL queries to validate MD5 checksums for a given DataFrame.

    This function constructs SQL queries to validate the MD5 checksums of the source and target DataFrames
    based on the provided compared DataFrame and index columns.

    Args:
        compared_df (pd.DataFrame): The DataFrame containing the compared MD5 checksums.
        fully_qualified_name (str): The fully qualified name of the source table being validated.
        target_fully_qualified_name (str): The fully qualified name of the target table being validated.
        source_index_column_collection (list[str]): A list of index columns used for comparison in the source DataFrame.
        target_index_column_collection (list[str]): A list of index columns used for comparison in the target DataFrame.
        context (Context): The execution context containing relevant configuration and runtime information.

    """
    source_conditions_collection = []
    target_conditions_collection = []
    for _, row in compared_df.iterrows():
        source_filter_conditions = _generate_filter_conditions(
            index_column_collection=source_index_column_collection, df_row=row
        )
        source_filter_conditions_endl = source_filter_conditions + "\n"
        source_conditions_collection.append(source_filter_conditions_endl)

        target_filter_conditions = _generate_filter_conditions(
            index_column_collection=target_index_column_collection, df_row=row
        )
        target_filter_conditions_endl = target_filter_conditions + "\n"
        target_conditions_collection.append(target_filter_conditions_endl)

    source_where_clause = " OR ".join(source_conditions_collection)

    source_query = MD5_REPORT_QUERY_TEMPLATE.format(
        fully_qualified_name=fully_qualified_name, condition=source_where_clause
    )

    target_where_clause = " OR ".join(target_conditions_collection)

    target_query = MD5_REPORT_QUERY_TEMPLATE.format(
        fully_qualified_name=target_fully_qualified_name, condition=target_where_clause
    )

    report_source_name = ROW_VALIDATION_DIFF_QUERY_NAME.format(
        platform=context.source_platform.value,
        fully_qualified_name=fully_qualified_name,
    )
    report_source_file = os.path.join(
        context.report_path,
        f"{context.run_start_time}_{report_source_name}",
    )

    report_target_name = ROW_VALIDATION_DIFF_QUERY_NAME.format(
        platform=context.target_platform.value,
        fully_qualified_name=target_fully_qualified_name,
    )

    report_target_file = os.path.join(
        context.report_path,
        f"{context.run_start_time}_{report_target_name}",
    )

    write_to_file(
        file_path=report_source_file,
        content=source_query,
    )

    write_to_file(
        file_path=report_target_file,
        content=target_query,
    )


def _generate_filter_conditions(
    index_column_collection: list[str], df_row: pd.Series
) -> str:
    filter_conditions = [
        generate_condition(column_name=index_column, value=df_row[index_column])
        for index_column in index_column_collection
    ]

    joined_filter_conditions = " AND ".join(filter_conditions)

    return joined_filter_conditions


def _generate_select_all_columns_query(
    fully_qualified_name: str, index_column_collection: list[str], df_row: pd.Series
) -> str:
    filter_conditions = _generate_filter_conditions(
        index_column_collection=index_column_collection, df_row=df_row
    )

    query = MD5_REPORT_QUERY_TEMPLATE.format(
        fully_qualified_name=fully_qualified_name, condition=filter_conditions
    )

    return query


def generate_condition(column_name: str, value: any, operator: str = "=") -> str:
    """Generate a SQL WHERE clause condition based on the column name, value, and operator.

    Args:
        column_name (str): The name of the column to filter on.
        value (Any): The value to compare against.
        operator (str): The comparison operator to use. Defaults to '='.

    Returns:
        str: A string representing the SQL WHERE clause condition.

    """
    if is_numeric(value):
        return f""""{column_name}" {operator} {value}"""
    else:
        return f""""{column_name}" {operator} '{value}'"""


def write_to_file(file_path: str, content: str) -> None:
    """Write content to a file with UTF-8 encoding.

    Creates the directory if it doesn't exist.

    Args:
        file_path (str): The full path to the file including directory and filename.
        content (str): The content to write to the file.

    """
    directory = os.path.dirname(file_path)
    if directory:
        os.makedirs(directory, exist_ok=True)

    with open(file_path, "a", encoding="utf-8") as f:
        f.write(content)
        f.write(NEWLINE)
