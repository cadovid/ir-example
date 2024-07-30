import json
import os
import pytest
import sys

from pydantic import ValidationError

sys.path.append(os.getcwd())
from main import (
    Request,
    Prediction,
    ZIP_PATH,
    RAW_DATA_PATH,
    DB_PATH,
    VECTORS_PATH,
)
from uuid import uuid4

# Dummy data for testing
dummy_request_data = {
    "zip_path": ZIP_PATH,
    "extract_to": RAW_DATA_PATH,
    "db_path": DB_PATH,
    "vectors_path": VECTORS_PATH,
    "query": "I want to listen to a podcast about entertainment industry, focusing on videogames",
    "top_n": 5,
    "min_score": 4.0,
    "max_score": 5.0,
    "min_date": "2019-07-07",
    "max_date": "2019-07-09",
    "boost_mode": True,
    "verbose": True,
}

dummy_prediction_data = {
    "prediction_id": uuid4(),
    "top_n_results": 5,
    "ranks": json.dumps([["result1", 1.0], ["result2", 0.87]]),
}


def test_request_model_validation():
    # Test successful creation
    request_model = Request(**dummy_request_data)
    assert request_model.zip_path == dummy_request_data["zip_path"]
    assert request_model.extract_to == dummy_request_data["extract_to"]
    assert request_model.db_path == dummy_request_data["db_path"]
    assert request_model.vectors_path == dummy_request_data["vectors_path"]
    assert request_model.query == dummy_request_data["query"]
    assert request_model.top_n == dummy_request_data["top_n"]
    assert request_model.min_score == dummy_request_data["min_score"]
    assert request_model.max_score == dummy_request_data["max_score"]
    assert request_model.min_date == dummy_request_data["min_date"]
    assert request_model.max_date == dummy_request_data["max_date"]
    assert request_model.boost_mode == dummy_request_data["boost_mode"]
    assert request_model.verbose == dummy_request_data["verbose"]

    # Test default values
    minimal_request_data = {
        "query": "A new query",
    }
    request_model = Request(**minimal_request_data)
    assert request_model.query == "A new query"
    assert request_model.zip_path == dummy_request_data["zip_path"]
    assert request_model.extract_to == dummy_request_data["extract_to"]
    assert request_model.db_path == dummy_request_data["db_path"]
    assert request_model.vectors_path == dummy_request_data["vectors_path"]
    assert request_model.top_n == dummy_request_data["top_n"]
    assert request_model.min_score is None
    assert request_model.max_score is None
    assert request_model.min_date is None
    assert request_model.max_date is None
    assert request_model.boost_mode is False
    assert request_model.verbose is False

    # Test validation error
    invalid_request_data = dummy_request_data.copy()
    invalid_request_data["top_n"] = "invalid_integer"
    with pytest.raises(ValidationError):
        Request(**invalid_request_data)


def test_prediction_model_validation():
    # Test successful creation
    prediction_model = Prediction(**dummy_prediction_data)
    assert (
        prediction_model.prediction_id
        == dummy_prediction_data["prediction_id"]
    )
    assert (
        prediction_model.top_n_results
        == dummy_prediction_data["top_n_results"]
    )
    assert prediction_model.ranks == dummy_prediction_data["ranks"]

    # Test validation error
    invalid_prediction_data = dummy_prediction_data.copy()
    invalid_prediction_data["top_n_results"] = "invalid_integer"
    with pytest.raises(ValidationError):
        Prediction(**invalid_prediction_data)

    # Test ranks must be a list of lists
    invalid_prediction_data["ranks"] = ["result1", "result2"]
    with pytest.raises(ValidationError):
        Prediction(**invalid_prediction_data)

    # Test default values
    minimal_prediction_data = {
        "top_n_results": 3,
        "ranks": json.dumps([["result1"], ["result2"]]),
    }
    prediction_model = Prediction(**minimal_prediction_data)
    assert isinstance(
        prediction_model.prediction_id, uuid4().__class__
    )  # Check that it's a UUID instance
    assert prediction_model.top_n_results == 3
    assert prediction_model.ranks == json.dumps([["result1"], ["result2"]])
