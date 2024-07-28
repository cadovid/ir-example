import json

from utils.common import extract_zip
from data.database import Database
from model.model import RetrievalModel


class CoreAPP:
    
    def __init__(self, zip_path, extract_to, db_path, vectors_path, query, top_n, min_score, max_score, min_date, max_date, boost_mode, verbose):
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
        extract_zip(self.zip_path, self.extract_to)
    
    def _set_database(self):
        self.db = Database(self.db_path, self.verbose)
    
    def get_records_from_database(self):
        self._set_database()
        self.db.show_all_tables()
        filtered_podcasts = self.db.filter_podcasts()
        
        joined_table = self.db.join_and_select(table1="categories",
                                               table2=filtered_podcasts,
                                               primary_key="podcast_id",
                                               columns_table1=["podcast_id", "category"],
                                               columns_table2=["podcast_id", "slug", "itunes_url", "title", "author", "description", "average_rating", "ratings_count", "scraped_at"],
                                               min_filter=self.min_score,
                                               max_filter=self.max_score,
                                               min_date=self.min_date,
                                               max_date=self.max_date
                                            )
        
        composed_table = self.db.add_composed_column(table=joined_table,
                                                    columns=["category", "slug", "title", "author", "description"],
                                                    new_column_name="full_info"
                                                    )
        self.records = self.db.fetch_column_records(table_name=composed_table,
                                                    columns=["podcast_id", "average_rating", "itunes_url", "full_info"]
                                                    )
        self.db.close_connection()
    
    def transform_records_from_database(self):
        self.records_dictionary = {}
        for item in self.records:
            self.records_dictionary.update({
                            str(item[0]): {"itunes_url": item[2],
                                           "average_rating": item[1],
                                           "text": item[3]
                                          }
                        })
    
    def _set_model(self):
        self.rm = RetrievalModel(self.vectors_path)
    
    def create_vectors_dictionary(self):
        self._set_model()
        self.rm.compute_vectors_dict(self.records_dictionary)
    
    def get_ranking(self):
        ranks = self.rm.rankings(self.query, top_n=self.top_n, boost_mode=self.boost_mode)
        return self._serialize(ranks)
    
    def _serialize(self, object):
        object = json.dumps(object, indent=4)
        return object
