import logging
import os
import zipfile


# Function to configure logger
def configure_logger(name: str = __name__) -> logging.Logger:
    """
    Configures and returns a logger with a standard setup.

    Args:
        name (str): The name of the logger. Defaults to the name of the module.

    Returns:
        logging.Logger: Configured logger.
    """
    # Create a logger
    logger = logging.getLogger(name)

    # Set the default logging level
    logger.setLevel(logging.DEBUG)

    # Create a console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    # Create a formatter and set it for the handlers
    formatter = logging.Formatter(
        "%(asctime)s - %(module)s - %(levelname)s - %(message)s"
    )
    ch.setFormatter(formatter)

    # Add the handlers to the logger
    logger.addHandler(ch)

    return logger


LOGGER = configure_logger()


# Function to check a directory
def ensure_directory_exists(directory_path):
    """
    Checks if a directory exists, and creates it if it does not.

    Args:
        directory_path (str): The path of the directory to check/create.

    Returns:
        str: The path of the directory.
    """
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
        LOGGER.info(f"Directory {directory_path} created.")
    else:
        LOGGER.info(f"Directory {directory_path} already exists.")
    return directory_path


# Function to extract a zip file
def extract_zip(zip_path, extract_to):
    """
    Extracts the contents of a zip file to the specified directory.

    Args:
        zip_path (str): The path to the zip file to extract.
        extract_to (str): The directory where the contents should be extracted.

    Returns:
        None
    """
    if os.path.isfile(extract_to + "/database.db"):
        LOGGER.info("Database .db file already present. Do not extract it.")
    else:
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(extract_to)
