import os
from typing import Optional
from uuid import UUID, uuid4

from fastapi import FastAPI
from pydantic import BaseModel

from core.core import CoreAPP
from utils.common import ensure_directory_exists

# Environment configuration
DATASET_PATH = os.environ.get(
    "DATASET_PATH", ensure_directory_exists(f"{os.getcwd()}/dataset")
)
RAW_DATA_PATH = os.environ.get(
    "RAW_DATA_PATH", ensure_directory_exists(f"{os.getcwd()}/dataset/raw_data")
)
ZIP_PATH = os.environ.get("ZIP_PATH", DATASET_PATH + "/podcastreviews.zip")
VECTORS_PATH = os.environ.get(
    "VECTORS_PATH", ensure_directory_exists(f"{os.getcwd()}/dataset/vectors")
)
DB_PATH = RAW_DATA_PATH + "/database.db"
QUERY = (
    "I want to listen to a podcast about entertainment industry, focusing on videogames"
)
TOP_N = 5


app = FastAPI()


class Request(BaseModel):
    """
    Request body schema for the /search/ endpoint.

    Attributes:
        zip_path (str): Path to the zip file. Defaults to ZIP_PATH.
        extract_to (str): Directory to extract the zip file to. Defaults to RAW_DATA_PATH.
        db_path (str): Path to the SQLite database file. Defaults to DB_PATH.
        vectors_path (str): Path to the vectors file. Defaults to VECTORS_PATH.
        query (str): Query for performing the search. Defaults to QUERY.
        top_n (int): Number of top results to return. Defaults to TOP_N.
        min_score (Optional[float]): Minimum score for filtering results. Defaults to None.
        max_score (Optional[float]): Maximum score for filtering results. Defaults to None.
        min_date (Optional[str]): Minimum date for filtering results. Defaults to None.
        max_date (Optional[str]): Maximum date for filtering results. Defaults to None.
        boost_mode (bool): Whether to use boost mode or not. Defaults to False.
        verbose (bool): Whether to enable verbose output. Defaults to False.
    """

    zip_path: str = ZIP_PATH
    extract_to: str = RAW_DATA_PATH
    db_path: str = DB_PATH
    vectors_path: str = VECTORS_PATH
    query: str = QUERY
    top_n: int = TOP_N
    min_score: Optional[float] = None
    max_score: Optional[float] = None
    min_date: Optional[str] = None
    max_date: Optional[str] = None
    boost_mode: bool = False
    verbose: bool = False


class Prediction(BaseModel):
    """
    Response body schema for the /search/ endpoint.

    Attributes:
        prediction_id (Optional[UUID]): Unique identifier for the prediction. Defaults to a new UUID.
        top_n_results (int): Number of top results returned.
        ranks (str): JSON string containing the ranked results.
    """

    prediction_id: Optional[UUID] = uuid4()
    top_n_results: int
    ranks: str


@app.get("/")
async def read_root():
    """
    Root endpoint for the application.

    Returns:
        str: A welcome message indicating that the IR example implementation is running.
    """
    return "Welcome to the IR example implementation"


@app.post("/search/", response_model=Prediction)
async def search_podcasts(request: Request):
    """
    Endpoint for searching podcasts based on the provided request parameters.

    Args:
        request (Request): Request body containing search parameters.

    Returns:
        Prediction: A Prediction object containing the prediction ID, number of top results, and ranked results.
    """
    core_app = CoreAPP(
        request.zip_path,
        request.extract_to,
        request.db_path,
        request.vectors_path,
        request.query,
        request.top_n,
        request.min_score,
        request.max_score,
        request.min_date,
        request.max_date,
        request.boost_mode,
        request.verbose,
    )
    ranks = core_app.main_logic()
    prediction = Prediction(
        prediction_id=uuid4(), top_n_results=request.top_n, ranks=ranks
    )
    return prediction
