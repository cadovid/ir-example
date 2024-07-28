import os
import zipfile

# Function to check a directory
def ensure_directory_exists(directory_path):
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
        print(f"Directory {directory_path} created.")
    else:
        print(f"Directory {directory_path} already exists.")
    return directory_path

# Function to extract a zip file
def extract_zip(zip_path, extract_to):
    if os.path.isfile(extract_to + "/database.db"):
        print("Database .db file already present. Do not extract it.")
    else:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
