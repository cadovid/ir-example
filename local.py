import argparse
import os

from core.core import CoreAPP
from utils.common import LOGGER, ensure_directory_exists

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


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Extract a zip file and insert its contents into an SQLite database."
    )
    parser.add_argument(
        "--zip_path",
        type=str,
        nargs="?",
        default=ZIP_PATH,
        help="Path to the zip file",
    )
    parser.add_argument(
        "--extract_to",
        type=str,
        nargs="?",
        default=RAW_DATA_PATH,
        help="Directory to extract the zip file to",
    )
    parser.add_argument(
        "--query",
        type=str,
        nargs="?",
        default=QUERY,
        help="Query to perform the retrieval based on",
    )
    parser.add_argument(
        "--top_n",
        type=int,
        nargs="?",
        default=TOP_N,
        help="Top n results to show based on similarity score",
    )
    parser.add_argument(
        "--min_score",
        type=float,
        nargs="?",
        default=None,
        help="Minimum rating score for the results",
    )
    parser.add_argument(
        "--max_score",
        type=float,
        nargs="?",
        default=None,
        help="Maximum rating score for the results",
    )
    parser.add_argument(
        "--min_date",
        type=str,
        nargs="?",
        default=None,
        help="Minimum date for the results",
    )
    parser.add_argument(
        "--max_date",
        type=str,
        nargs="?",
        default=None,
        help="Maximum date for the results",
    )
    parser.add_argument(
        "--boost_mode",
        action="store_true",
        help="Ranks higher results with a bigger average rating score",
    )
    parser.add_argument(
        "--verbose", action="store_true", help="Verbosity of the execution"
    )

    args = parser.parse_args()

    core_app = CoreAPP(
        args.zip_path,
        args.extract_to,
        DB_PATH,
        VECTORS_PATH,
        args.query,
        args.top_n,
        args.min_score,
        args.max_score,
        args.min_date,
        args.max_date,
        args.boost_mode,
        args.verbose,
    )
    ranks = core_app.main_logic()
    LOGGER.info(ranks)
