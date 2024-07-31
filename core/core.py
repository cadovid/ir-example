import json

from data.database import Database
from model.model import RetrievalModel
from utils.common import extract_zip


class CoreAPP:
    """
    Core application class for handling podcast search and ranking.

    This class manages the extraction of a zip file, interaction with a database, transformation of records,
    computation of vectors, and retrieval of ranked podcast results.

    Attributes:
        zip_path (str): Path to the zip file containing the podcasts data.
        extract_to (str): Directory where the zip file will be extracted.
        db_path (str): Path to the SQLite database.
        vectors_path (str): Path to the vectors file used for ranking.
        query (str): Query string to search for podcasts.
        top_n (int): Number of top results to return based on similarity.
        min_score (Optional[float]): Minimum rating score for filtering results.
        max_score (Optional[float]): Maximum rating score for filtering results.
        min_date (Optional[str]): Minimum date for filtering results.
        max_date (Optional[str]): Maximum date for filtering results.
        boost_mode (bool): Whether to use boost mode for ranking.
        verbose (bool): Whether to enable verbose output.
        records (list): List of records fetched from the database.
        records_dictionary (dict): Dictionary of records transformed from the database.
        rm (RetrievalModel): Instance of the RetrievalModel used for ranking.
    """

    def __init__(
        self,
        zip_path,
        extract_to,
        db_path,
        vectors_path,
        query,
        top_n,
        min_score,
        max_score,
        min_date,
        max_date,
        boost_mode,
        verbose,
    ):
        """
        Initializes the CoreAPP instance.

        Args:
            zip_path (str): Path to the zip file.
            extract_to (str): Directory to extract the zip file to.
            db_path (str): Path to the SQLite database file.
            vectors_path (str): Path to the vectors file.
            query (str): Query string for searching podcasts.
            top_n (int): Number of top results to return.
            min_score (Optional[float]): Minimum score for filtering results.
            max_score (Optional[float]): Maximum score for filtering results.
            min_date (Optional[str]): Minimum date for filtering results.
            max_date (Optional[str]): Maximum date for filtering results.
            boost_mode (bool): Whether to enable boost mode.
            verbose (bool): Whether to enable verbose logging.
        """
        self.zip_path = zip_path
        self.extract_to = extract_to
        self.db_path = db_path
        self.vectors_path = vectors_path
        self.query = query
        self.top_n = top_n
        self.min_score = min_score
        self.max_score = max_score
        self.min_date = min_date
        self.max_date = max_date
        self.boost_mode = boost_mode
        self.verbose = verbose
        self._extract_zip_file()

    def _extract_zip_file(self):
        """
        Extracts the zip file specified by `self.zip_path` to the directory specified by `self.extract_to`.

        Uses the `extract_zip` function from the `utils.common` module.
        """
        extract_zip(self.zip_path, self.extract_to)

    def _set_database(self):
        """
        Initializes the `Database` instance with `self.db_path` and `self.verbose`.
        """
        self.db = Database(self.db_path, self.verbose)

    def _get_records_from_database(self):
        """
        Fetches and processes records from the database.

        - Initializes the database connection.
        - Retrieves and filters podcasts.
        - Joins tables and selects relevant columns.
        - Adds a composed column to the table.
        - Fetches the final records.
        - Closes the database connection.
        """
        self._set_database()
        self.db.show_all_tables()
        filtered_podcasts = self.db.filter_podcasts()

        joined_table = self.db.join_and_select(
            table1="categories",
            table2=filtered_podcasts,
            primary_key="podcast_id",
            columns_table1=["podcast_id", "category"],
            columns_table2=[
                "podcast_id",
                "slug",
                "itunes_url",
                "title",
                "author",
                "description",
                "average_rating",
                "ratings_count",
                "scraped_at",
            ],
            min_filter=self.min_score,
            max_filter=self.max_score,
            min_date=self.min_date,
            max_date=self.max_date,
        )

        composed_table = self.db.add_composed_column(
            table=joined_table,
            columns=["category", "slug", "title", "author", "description"],
            new_column_name="full_info",
        )
        self.records = self.db.fetch_column_records(
            table_name=composed_table,
            columns=[
                "podcast_id",
                "average_rating",
                "itunes_url",
                "full_info",
            ],
        )
        self.db.close_connection()

    def _transform_records_from_database(self):
        """
        Transforms the records fetched from the database into a dictionary format.

        The dictionary maps podcast IDs to a dictionary of attributes including `itunes_url`, `average_rating`, and `text`.
        """
        self.records_dictionary = {}
        for item in self.records:
            self.records_dictionary.update(
                {
                    str(item[0]): {
                        "itunes_url": item[2],
                        "average_rating": item[1],
                        "text": item[3],
                    }
                }
            )

    def _set_model(self):
        """
        Initializes the `RetrievalModel` instance with `self.vectors_path`.
        """
        self.rm = RetrievalModel(self.vectors_path)

    def _create_vectors_dictionary(self):
        """
        Computes the vectors dictionary using the `RetrievalModel` instance.

        Updates the vectors dictionary in `self.rm` with `self.records_dictionary`.
        """
        self._set_model()
        self.rm.compute_vectors_dict(self.records_dictionary)

    def _get_ranking(self):
        """
        Retrieves and ranks the podcasts based on the query.

        Uses the `RetrievalModel` instance to get rankings and serializes them.

        Returns:
            str: JSON string of the ranked results.
        """
        ranks = self.rm.rankings(
            self.query, top_n=self.top_n, boost_mode=self.boost_mode
        )
        return self._serialize(ranks)

    def _serialize(self, object):
        """
        Serializes an object to a JSON formatted string.

        Args:
            object: The object to be serialized.

        Returns:
            str: JSON formatted string of the object.
        """
        object = json.dumps(object, indent=4)
        return object

    def main_logic(self):
        """
        Executes the main logic of the CoreAPP.

        - Fetches and processes records from the database.
        - Transforms records into a dictionary.
        - Creates vectors dictionary.
        - Retrieves and returns the ranked results.

        Returns:
            str: JSON string of the ranked results.
        """
        self._get_records_from_database()
        self._transform_records_from_database()
        self._create_vectors_dictionary()
        ranks = self._get_ranking()
        return ranks
