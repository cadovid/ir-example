import os
import pytest
import sys

from fastapi.testclient import TestClient
sys.path.append(os.getcwd())
from main import app


client = TestClient(app)


# Dummy data for testing
dummy_request = {
    "query": "I want to listen to a podcast about entertainment industry, focusing on videogames",
    "top_n": 5,
    "min_score": 3.0,
    "max_score": 5.0,
    "boost_mode": True
}


@pytest.fixture
def setup_client():
    with TestClient(app) as client:
        yield client

def test_read_root(setup_client):
    response = setup_client.get("/")
    assert response.status_code == 200
    assert response.json() == "Welcome to the IR example implementation"

def test_search_podcasts(setup_client):
    response = setup_client.post("/search/", json=dummy_request)
    assert response.status_code == 200
    data = response.json()
    assert "prediction_id" in data
    assert data["top_n_results"] == dummy_request["top_n"]
    assert isinstance(data["ranks"], str)

def test_search_podcasts_with_optional_parameters(setup_client):
    modified_request = dummy_request.copy()
    modified_request["min_score"] = None
    modified_request["max_score"] = None
    modified_request["min_date"] = None
    modified_request["max_date"] = None
    response = setup_client.post("/search/", json=modified_request)
    assert response.status_code == 200
    data = response.json()
    assert "prediction_id" in data
    assert data["top_n_results"] == modified_request["top_n"]
    assert isinstance(data["ranks"], str)

def test_search_podcasts_with_invalid_data(setup_client):
    invalid_request = dummy_request.copy()
    invalid_request["boost_mode"] = -1
    response = setup_client.post("/search/", json=invalid_request)
    assert response.status_code == 422
