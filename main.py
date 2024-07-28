import json
import os
import argparse

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


# Main function
def main(zip_path, extract_to, db_path, vectors_path, query, top_n, verbose=True):
    
    core_app = CoreAPP(zip_path, extract_to, db_path, vectors_path, query, top_n, verbose)
    core_app.get_records_from_database()
    core_app.transform_records_from_database()
    core_app.create_vectors_dictionary()
    ranks = core_app.get_ranking()
    
    return ranks


if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description="Extract a zip file and insert its contents into an SQLite database.")
    parser.add_argument('--zip_path', type=str, nargs='?', default=ZIP_PATH, help='Path to the zip file')
    parser.add_argument('--extract_to', type=str, nargs='?', default=RAW_DATA_PATH, help='Directory to extract the zip file to')
    parser.add_argument('--query', type=str, nargs='?', default=QUERY, help='Query to perform the retrieval based on')
    parser.add_argument('--top_n', type=int, nargs='?', default=TOP_N, help='Top n results to show based on similarity score')
    
    args = parser.parse_args()
    
    ranks = main(args.zip_path, args.extract_to, DB_PATH, VECTORS_PATH, args.query, args.top_n)
    print(ranks)
