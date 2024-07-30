import os
import pytest
import json
import sys

sys.path.append(os.getcwd())
from core.core import CoreAPP
from main import ZIP_PATH, RAW_DATA_PATH, DB_PATH, VECTORS_PATH


@pytest.fixture
def core_app():
    zip_path = ZIP_PATH
    extract_to = RAW_DATA_PATH
    db_path = DB_PATH
    vectors_path = VECTORS_PATH
    query = "I want to listen to a podcast about entertainment industry, focusing on videogames"
    top_n = 5
    min_score = 4.0
    max_score = 5.0
    min_date = "2019-07-07"
    max_date = "2019-07-09"
    boost_mode = True
    verbose = True
    return CoreAPP(zip_path, extract_to, db_path, vectors_path, query, top_n, min_score, max_score, min_date, max_date, boost_mode, verbose)

def test_extract_zip_file(mocker, core_app):
    mock_extract_zip = mocker.patch('core.core.extract_zip')
    core_app._extract_zip_file()
    mock_extract_zip.assert_called_once_with(core_app.zip_path, core_app.extract_to)

def test_set_database(mocker, core_app):
    mock_database = mocker.patch('core.core.Database')
    core_app._set_database()
    mock_database.assert_called_once_with(core_app.db_path, core_app.verbose)
    assert core_app.db is not None

def test_get_records_from_database(mocker, core_app):
    mock_database = mocker.patch('core.core.Database')
    mock_db_instance = mock_database.return_value
    mock_db_instance.filter_podcasts.return_value = "filtered_podcasts"
    mock_db_instance.join_and_select.return_value = "joined_table"
    mock_db_instance.add_composed_column.return_value = "composed_table"
    mock_db_instance.fetch_column_records.return_value = [
        (1, 4.5, "https://example.com", "info1"),
        (2, 4.2, "https://example.com", "info2")
    ]

    core_app._get_records_from_database()

    mock_database.assert_called_once_with(core_app.db_path, core_app.verbose)
    mock_db_instance.show_all_tables.assert_called_once()
    mock_db_instance.filter_podcasts.assert_called_once()
    mock_db_instance.join_and_select.assert_called_once_with(
        table1="categories",
        table2="filtered_podcasts",
        primary_key="podcast_id",
        columns_table1=["podcast_id", "category"],
        columns_table2=["podcast_id", "slug", "itunes_url", "title", "author", "description", "average_rating", "ratings_count", "scraped_at"],
        min_filter=core_app.min_score,
        max_filter=core_app.max_score,
        min_date=core_app.min_date,
        max_date=core_app.max_date
    )
    mock_db_instance.add_composed_column.assert_called_once_with(
        table="joined_table",
        columns=["category", "slug", "title", "author", "description"],
        new_column_name="full_info"
    )
    mock_db_instance.fetch_column_records.assert_called_once_with(
        table_name="composed_table",
        columns=["podcast_id", "average_rating", "itunes_url", "full_info"]
    )
    mock_db_instance.close_connection.assert_called_once()
    assert core_app.records == [
        (1, 4.5, "https://example.com", "info1"),
        (2, 4.2, "https://example.com", "info2")
    ]

def test_transform_records_from_database(core_app):
    core_app.records = [
        (1, 4.5, "https://example.com", "info1"),
        (2, 4.2, "https://example.com", "info2")
    ]
    core_app._transform_records_from_database()
    expected_dictionary = {
        "1": {"itunes_url": "https://example.com", "average_rating": 4.5, "text": "info1"},
        "2": {"itunes_url": "https://example.com", "average_rating": 4.2, "text": "info2"}
    }
    assert core_app.records_dictionary == expected_dictionary

def test_set_model(mocker, core_app):
    mock_retrieval_model = mocker.patch('core.core.RetrievalModel')
    core_app._set_model()
    mock_retrieval_model.assert_called_once_with(core_app.vectors_path)
    assert core_app.rm is not None

def test_create_vectors_dictionary(mocker, core_app):
    mock_retrieval_model = mocker.patch('core.core.RetrievalModel')
    mock_rm_instance = mock_retrieval_model.return_value
    core_app.records_dictionary = {
        "1": {"itunes_url": "https://example.com", "average_rating": 4.5, "text": "info1"},
        "2": {"itunes_url": "https://example.com", "average_rating": 4.2, "text": "info2"}
    }
    core_app._create_vectors_dictionary()
    mock_retrieval_model.assert_called_once_with(core_app.vectors_path)
    mock_rm_instance.compute_vectors_dict.assert_called_once_with(core_app.records_dictionary)

def test_serialize(core_app):
    obj = {"key": "value"}
    serialized_obj = core_app._serialize(obj)
    expected_serialized_obj = json.dumps(obj, indent=4)
    assert serialized_obj == expected_serialized_obj

def test_main_logic(mocker, core_app):
    mock_get_records_from_database = mocker.patch.object(core_app, '_get_records_from_database')
    mock_transform_records_from_database = mocker.patch.object(core_app, '_transform_records_from_database')
    mock_create_vectors_dictionary = mocker.patch.object(core_app, '_create_vectors_dictionary')
    mock_get_ranking = mocker.patch.object(core_app, '_get_ranking')
    mock_get_ranking.return_value = "ranks"

    result = core_app.main_logic()

    mock_get_records_from_database.assert_called_once()
    mock_transform_records_from_database.assert_called_once()
    mock_create_vectors_dictionary.assert_called_once()
    mock_get_ranking.assert_called_once()
    assert result == "ranks"
