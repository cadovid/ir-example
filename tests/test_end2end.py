import json
import os
import sys

import pytest
from fastapi.testclient import TestClient

sys.path.append(os.getcwd())
from main import DB_PATH, QUERY, RAW_DATA_PATH, TOP_N, VECTORS_PATH, ZIP_PATH, app


@pytest.fixture(scope="module")
def setup_environment():
    zip_path = ZIP_PATH
    extract_path = RAW_DATA_PATH
    real_db_path = DB_PATH
    vectors_path = VECTORS_PATH
    query = QUERY
    top_n = TOP_N
    min_score = 3.0
    max_score = 4.0
    min_date = "2019-07-07"
    max_date = "2019-07-08"
    boost_mode = False
    verbose = False

    for path in [zip_path, real_db_path]:
        if not os.path.isfile(path):
            pytest.fail(f"File not found at {path}")

    return {
        "zip_path": zip_path,
        "extract_to": extract_path,
        "db_path": real_db_path,
        "vectors_path": vectors_path,
        "query": query,
        "top_n": top_n,
        "min_score": min_score,
        "max_score": max_score,
        "min_date": min_date,
        "max_date": max_date,
        "boost_mode": boost_mode,
        "verbose": verbose,
    }


@pytest.fixture(scope="module")
def client(setup_environment):
    with TestClient(app) as client:
        yield client


def test_search_podcasts(client, setup_environment):
    # Prepare the request payload
    payload = {
        "zip_path": setup_environment["zip_path"],
        "extract_to": setup_environment["extract_to"],
        "db_path": setup_environment["db_path"],
        "vectors_path": setup_environment["vectors_path"],
        "query": setup_environment["query"],
        "top_n": setup_environment["top_n"],
        "min_score": setup_environment["min_score"],
        "max_score": setup_environment["max_score"],
        "min_date": setup_environment["min_date"],
        "max_date": setup_environment["max_date"],
        "boost_mode": setup_environment["boost_mode"],
        "verbose": setup_environment["verbose"],
    }

    # Perform the API request
    response = client.post("/search/", json=payload)

    # Validate response
    assert response.status_code == 200
    response_json = response.json()
    assert "prediction_id" in response_json
    assert "top_n_results" in response_json
    assert "ranks" in response_json
    assert isinstance(response_json["top_n_results"], int)
    assert isinstance(response_json["ranks"], str)

    # Additional assertions depending on expected results
    response_ranks = response_json["ranks"]
    response_ranks = json.loads(response_ranks)
    assert response_json["top_n_results"] == setup_environment["top_n"]
    assert len(response_ranks) == setup_environment["top_n"]
    assert type(response_ranks[0][0]) == str  # Assert url is valid
    assert type(response_ranks[0][1][0]) == float  # Assert score is valid
    assert (
        response_ranks[0][1]
        > response_ranks[1][1]
        > response_ranks[2][1]
        > response_ranks[3][1]
        > response_ranks[4][1]
    )  # Assert results are valid


def test_boost_mode_difference(client, setup_environment):
    # Prepare payload with boost_mode=False
    payload_no_boost = setup_environment.copy()
    payload_no_boost["boost_mode"] = False

    # Perform the API request with boost_mode=False
    response_no_boost = client.post("/search/", json=payload_no_boost)
    assert response_no_boost.status_code == 200
    response_no_boost_json = response_no_boost.json()
    response_no_boost_ranks = response_no_boost_json["ranks"]
    response_no_boost_ranks = json.loads(response_no_boost_ranks)

    # Prepare payload with boost_mode=True
    payload_with_boost = setup_environment.copy()
    payload_with_boost["boost_mode"] = True

    # Perform the API request with boost_mode=True
    response_with_boost = client.post("/search/", json=payload_with_boost)
    assert response_with_boost.status_code == 200
    response_with_boost_json = response_with_boost.json()
    response_with_boost_ranks = response_with_boost_json["ranks"]
    response_with_boost_ranks = json.loads(response_with_boost_ranks)

    # Validate that results are different
    assert response_no_boost_ranks != response_with_boost_ranks
