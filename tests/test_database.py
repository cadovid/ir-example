import os
import sys

import duckdb
import pytest

sys.path.append(os.getcwd())
from unittest.mock import MagicMock, patch

from data.database import Database


@pytest.fixture
def db():
    with patch("duckdb.connect") as mock_connect:
        mock_connect.return_value = MagicMock()
        db_instance = Database(db_path=os.path.join(os.path.dirname(__file__), "test.db"), verbose=True)
        yield db_instance
        db_instance.close_connection()


def test_init(db):
    assert db.db_path == os.path.join(os.path.dirname(__file__), "test.db")
    assert db.verbose is True
    db.connection.close.assert_not_called()  # Ensure close isn't called on init


def test_close_connection(db):
    db.close_connection()
    db.connection.close.assert_called_once()


def test_show_table(db, mocker):
    mock_table = db.connection.table.return_value
    mock_table.limit.return_value.show = mocker.Mock()

    db.show_table("test_table", limit=3)

    db.connection.table.assert_called_with("test_table")
    mock_table.limit.assert_called_with(3)
    mock_table.limit().show.assert_called_once()


def test_show_all_tables(db, mocker):
    mock_show_table = mocker.patch.object(db, "show_table")

    db.show_all_tables()

    mock_show_table.assert_any_call("categories")
    mock_show_table.assert_any_call("podcasts")
    mock_show_table.assert_any_call("reviews")


def test_filter_podcasts(db):
    mock_table = db.connection.table.return_value
    mock_filter = mock_table.filter.return_value

    filtered_podcasts = db.filter_podcasts()

    db.connection.table.assert_called_with("podcasts")
    mock_table.filter.assert_called_with(
        "average_rating IS NOT NULL AND scraped_at IS NOT NULL"
    )
    mock_filter.limit().show.assert_called_once()
    assert filtered_podcasts == mock_filter


def test_join_and_select(db):
    # Mocking table objects
    mock_table1 = db.connection.table.return_value
    mock_table2 = db.connection.table.return_value

    # Mocking the return values for methods
    mock_selected_table1 = mock_table1.project.return_value
    mock_selected_table2 = mock_table2.project.return_value
    mock_filtered_table2 = mock_selected_table2.filter.return_value
    mock_joined_table = mock_selected_table1.join.return_value

    # Call the method
    db.join_and_select(
        "categories",
        "podcasts",
        "podcast_id",
        ["podcast_id", "category"],
        ["podcast_id", "slug"],
        min_filter=1,
        max_filter=5,
        min_date="2019-07-07",
        max_date="2019-07-07",
    )

    # Assertions
    db.connection.table.assert_any_call("categories")
    db.connection.table.assert_any_call("podcasts")

    # Assert correct project call on table1 and table2
    mock_table2.project.assert_called_with("podcast_id, slug")

    # Assert filter call on selected_table2
    mock_selected_table2.filter.assert_called_with(
        "average_rating >= 1 AND average_rating <= 5 AND scraped_at >= '2019-07-07' AND scraped_at <= '2019-07-07'"
    )

    # Assert join call
    mock_selected_table1.join.assert_called_with(mock_filtered_table2, "podcast_id")


def test_add_composed_column(db):
    mock_table = MagicMock()
    mock_project = mock_table.project

    db.add_composed_column(mock_table, ["category", "slug"], "full_info")

    mock_project.assert_called_once_with(
        "*, COALESCE(category, '') || ' ' || COALESCE(slug, '') AS full_info"
    )


def test_fetch_column_records(db):
    mock_table = db.connection.table.return_value
    mock_project = mock_table.project.return_value
    mock_fetchall = mock_project.fetchall

    db.fetch_column_records("test_table", ["column1", "column2"])

    db.connection.table.assert_called_with("test_table")
    mock_table.project.assert_called_with("column1, column2")
    mock_fetchall.assert_called_once()

    mock_relation = MagicMock(spec=duckdb.DuckDBPyRelation)
    db.fetch_column_records(mock_relation, ["column1", "column2"])

    mock_relation.project.assert_called_with("column1, column2")
    mock_relation.project().fetchall.assert_called_once()
