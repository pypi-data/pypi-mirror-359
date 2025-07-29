import pytest
from snowflake.snowflake_data_validation.utils.model.column_metadata import (
    ColumnMetadata,
)
from snowflake.snowflake_data_validation.utils.model.table_context import TableContext


def make_col(name):
    return ColumnMetadata(
        name=name,
        data_type="VARCHAR",
        nullable=True,
        is_primary_key=False,
        calculated_column_size_in_bytes=0,
        properties={},
    )


def test_get_columns_to_validate_inclusion():
    cols = [make_col("A"), make_col("B"), make_col("C")]
    # Only include B and C
    test_context = TableContext(
        platform="snowflake",
        origin="test_origin",
        fully_qualified_name="test_table",
        database_name="test_db",
        schema_name="test_schema",
        table_name="test_table",
        columns=cols,
        where_clause="",
        has_where_clause=False,
        use_as_exclude_list=False,
        column_selection_list=["B", "C"],
        templates_loader_manager=None,
        sql_generator=None,
        run_id="test_run",
        run_start_time=None,
    )
    result = test_context.columns_to_validate
    assert [c.name for c in result] == ["B", "C"]


def test_get_columns_to_validate_exclusion():
    cols = [make_col("A"), make_col("B"), make_col("C")]
    # Exclude B
    test_context = TableContext(
        platform="snowflake",
        origin="test_origin",
        fully_qualified_name="test_table",
        database_name="test_db",
        schema_name="test_schema",
        table_name="test_table",
        columns=cols,
        where_clause="",
        has_where_clause=False,
        use_as_exclude_list=True,
        column_selection_list=["B"],
        templates_loader_manager=None,
        sql_generator=None,
        run_id="test_run",
        run_start_time=None,
    )
    result = test_context.columns_to_validate
    # Should return A and C, excluding B
    assert [c.name for c in result] == ["A", "C"]


def test_get_columns_to_validate_empty_column_list():
    cols = [make_col("A"), make_col("B")]
    test_context = TableContext(
        platform="snowflake",
        origin="test_origin",
        fully_qualified_name="test_table",
        database_name="test_db",
        schema_name="test_schema",
        table_name="test_table",
        columns=cols,
        where_clause="",
        has_where_clause=False,
        use_as_exclude_list=False,
        column_selection_list=[],
        templates_loader_manager=None,
        sql_generator=None,
        run_id="test_run",
        run_start_time=None,
    )
    # No filter, should return all
    result = test_context.columns_to_validate
    assert [c.name for c in result] == ["A", "B"]


def test_get_columns_to_validate_regex():
    cols = [make_col("foo"), make_col("bar"), make_col("baz")]
    test_context = TableContext(
        platform="snowflake",
        origin="test_origin",
        fully_qualified_name="test_table",
        database_name="test_db",
        schema_name="test_schema",
        table_name="test_table",
        columns=cols,
        where_clause="",
        has_where_clause=False,
        use_as_exclude_list=False,
        column_selection_list=['r"^ba"'],
        templates_loader_manager=None,
        sql_generator=None,
        run_id="test_run",
        run_start_time=None,
    )

    # Regex for all names starting with 'ba'
    result = test_context.columns_to_validate
    assert [c.name for c in result] == ["BAR", "BAZ"]


def test_get_columns_to_validate_exclusion_regex():
    cols = [make_col("foo"), make_col("bar"), make_col("baz")]
    # Exclude all names starting with 'ba'
    test_context = TableContext(
        platform="snowflake",
        origin="test_origin",
        fully_qualified_name="test_table",
        database_name="test_db",
        schema_name="test_schema",
        table_name="test_table",
        columns=cols,
        where_clause="",
        has_where_clause=False,
        use_as_exclude_list=True,
        column_selection_list=['r"^ba"'],
        templates_loader_manager=None,
        sql_generator=None,
        run_id="test_run",
        run_start_time=None,
        case_sensitive=True,
    )
    result = test_context.columns_to_validate
    assert [c.name for c in result] == ["foo"]
