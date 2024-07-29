import os

from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
from uuid import uuid4, UUID
from core.core import CoreAPP
from utils.common import ensure_directory_exists


# Environment configuration
DATASET_PATH = os.environ.get("DATASET_PATH", ensure_directory_exists(f"{os.getcwd()}/dataset"))
RAW_DATA_PATH = os.environ.get("RAW_DATA_PATH", ensure_directory_exists(f"{os.getcwd()}/dataset/raw_data"))
ZIP_PATH = os.environ.get("ZIP_PATH", DATASET_PATH + "/archive.zip")
VECTORS_PATH = os.environ.get("VECTORS_PATH", ensure_directory_exists(f"{os.getcwd()}/dataset/vectors"))
DB_PATH = RAW_DATA_PATH + "/database.db"
QUERY = "I want to listen to a podcast about entertainment industry, focusing on videogames"
TOP_N = 5


app = FastAPI()


class Request(BaseModel):
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
    prediction_id: Optional[UUID] = uuid4()
    top_n_results: int
    ranks: str
    

@app.get("/")
async def read_root():
    return "Welcome to the IR example implementation"

@app.post("/search/", response_model=Prediction)
async def search_podcasts(request: Request):
    core_app = CoreAPP(request.zip_path,
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
                       request.verbose
                       )
    ranks = core_app.main_logic()
    prediction = Prediction(prediction_id=uuid4(),
                            top_n_results=request.top_n,
                            ranks=ranks
                            )
    return prediction
