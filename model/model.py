import re

import gensim
import nltk
import numpy as np
import scipy

from utils.common import LOGGER


class RetrievalModel:
    """
    A class to handle retrieval operations using word embeddings.

    This class loads pre-trained word vectors, processes text data, and computes similarity
    between query vectors and document vectors for ranking purposes.

    Attributes:
        model (gensim.models.KeyedVectors): Pre-trained word vectors model.
        vectors_path (str): Path to the word vectors file.
        stopword_list (list): List of English stopwords.
        vectors_dict (dict): Dictionary of podcast vectors and metadata.
    """

    def __init__(self, vectors_path):
        """
        Initializes the RetrievalModel instance.

        Args:
            vectors_path (str): Directory path where the word vectors file is located.
        """
        self.model = None
        self.vectors_path = vectors_path + "/GoogleNews-vectors-negative300.bin.gz"
        nltk.download("stopwords")
        nltk.download("punkt")

    def _create_stopwords(self):
        """
        Creates a list of English stopwords and logs the creation.
        """
        self.stopword_list = nltk.corpus.stopwords.words("english")
        LOGGER.info("English list of stopwords created")

    def _load_vectors(self):
        """
        Loads the word vectors model from the specified path and logs the action.
        """
        self.model = gensim.models.KeyedVectors.load_word2vec_format(
            self.vectors_path, binary=True, limit=500000
        )
        LOGGER.info(f"Vectors loaded from {self.vectors_path}")

    def _data_clean(self, text):
        """
        Cleans and processes the input text.

        Args:
            text (list of str): List of words or tokens to be cleaned.

        Returns:
            str: Cleaned and filtered text with stopwords removed.
        """
        for index, word in enumerate(text):
            if "-" in word:
                word = word.replace("-", " ")
                word = word.split()
                text[index] = word
        flattened_list = []
        for item in text:
            if isinstance(item, list):
                flattened_list.extend(item)
            else:
                flattened_list.append(item)
        pattern = r"[^a-zA-Z0-9\s]"
        flattened_list = re.sub(pattern, "", " ".join(flattened_list))
        tokens = [token.strip() for token in flattened_list.split()]
        filtered = [
            token for token in tokens if token.lower() not in self.stopword_list
        ]
        filtered = " ".join(filtered)
        return filtered

    def _tokenize_text(self, text):
        """
        Tokenizes and cleans the input text.

        Args:
            text (str): Input text to be tokenized and cleaned.

        Returns:
            str: Cleaned and tokenized text.
        """
        return self._data_clean(nltk.word_tokenize(text))

    def _embeddings(self, word):
        """
        Retrieves the word embedding vector for a given word.

        Args:
            word (str): The word for which the embedding vector is retrieved.

        Returns:
            numpy.ndarray: Word embedding vector. Returns a zero vector if the word is not in the model.
        """
        if word in self.model.key_to_index:
            return self.model.get_vector(word)
        else:
            return np.zeros(300)

    def compute_vectors_dict(self, records_dictionary):
        """
        Computes the average vector representation for each podcast in the records dictionary.

        Args:
            records_dictionary (dict): Dictionary where keys are podcast IDs and values are dictionaries
                                        containing 'itunes_url', 'average_rating', and 'text'.

        Updates:
            self.vectors_dict: Dictionary with podcast IDs as keys and vectors and metadata as values.
        """
        self._create_stopwords()
        self._load_vectors()
        vectors_dict = {}
        for podcast_id, value in records_dictionary.items():
            average_vector = np.mean(
                np.array(
                    [
                        self._embeddings(x)
                        for x in self._tokenize_text(value["text"]).split()
                    ]
                ),
                axis=0,
            )
            output = {
                podcast_id: {
                    "itunes_url": value["itunes_url"],
                    "average_rating": value["average_rating"],
                    "average_vector": (average_vector),
                }
            }
            vectors_dict.update(output)
        self.vectors_dict = vectors_dict
        LOGGER.info(
            f"Internal vectors dictionary created with a total len of {len(self.vectors_dict)}"
        )

    def _get_similarity(self, query_embedding, average_vec):
        """
        Computes the cosine similarity between the query embedding and a document vector.

        Args:
            query_embedding (numpy.ndarray): The vector representation of the query.
            average_vec (numpy.ndarray): The vector representation of the document.

        Returns:
            list: List containing the cosine similarity score.
        """
        sim = [(1 - scipy.spatial.distance.cosine(query_embedding, average_vec))]
        return sim

    def rankings(self, query, top_n, boost_mode):
        """
        Ranks the podcasts based on the similarity of their vectors to the query vector.

        Args:
            query (str): The query text for which rankings are computed.
            top_n (int): The number of top results to return.
            boost_mode (bool): If True, rank higher results with a bigger average rating score.

        Returns:
            list: List of tuples where each tuple contains the podcast URL and similarity score.
        """
        query_words = np.mean(
            np.array(
                [self._embeddings(x) for x in nltk.word_tokenize(query.lower())],
                dtype=float,
            ),
            axis=0,
        )
        ranks = []
        if not boost_mode:
            for k, v in self.vectors_dict.items():
                ranks.append(
                    (
                        v["itunes_url"],
                        self._get_similarity(query_words, v["average_vector"]),
                    )
                )
        else:
            for k, v in self.vectors_dict.items():
                ranks.append(
                    (
                        v["itunes_url"],
                        self._get_similarity(query_words, v["average_vector"])[0]
                        * v["average_rating"],
                    )
                )
        ranks = sorted(ranks, key=lambda t: t[1], reverse=True)
        return ranks[:top_n]
