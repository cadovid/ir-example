import os
import pytest
import sys

from unittest.mock import MagicMock, patch
import numpy as np

sys.path.append(os.getcwd())
from model.model import RetrievalModel


@pytest.fixture
def retrieval_model():
    with patch('model.model.gensim') as mock_gensim, \
         patch('model.model.nltk') as mock_nltk, \
         patch('model.model.scipy') as mock_scipy:
        
        # Mocking gensim KeyedVectors
        mock_keyed_vectors = MagicMock()
        mock_gensim.models.KeyedVectors.load_word2vec_format.return_value = mock_keyed_vectors
        mock_keyed_vectors.key_to_index = {'test': 0}
        mock_keyed_vectors.get_vector.return_value = np.array([1.0] * 300)
        
        # Mocking nltk downloads
        mock_nltk.download = MagicMock()
        mock_nltk.corpus.stopwords.words.return_value = ['the', 'is', 'in', 'and']
        mock_nltk.word_tokenize = MagicMock(side_effect=lambda text: text.split())

        # Mocking scipy distance
        mock_scipy.spatial.distance.cosine = MagicMock(return_value=0.1)

        model = RetrievalModel(vectors_path='/mock/path')

        yield model

def test_create_stopwords(retrieval_model):
    retrieval_model._create_stopwords()
    assert retrieval_model.stopword_list == ['the', 'is', 'in', 'and']

def test_load_vectors(retrieval_model):
    retrieval_model._load_vectors()
    assert retrieval_model.model is not None

def test_data_clean(retrieval_model):
    retrieval_model._create_stopwords()
    
    text = ["This", "is", "a", "test-", "example"]
    cleaned_text = retrieval_model._data_clean(text)
    assert cleaned_text == "This a test example"

def test_tokenize_text(retrieval_model):
    retrieval_model._create_stopwords()
    text = "This is a test example"
    tokenized_text = retrieval_model._tokenize_text(text)
    assert tokenized_text == "This a test example"

def test_embeddings(retrieval_model):
    retrieval_model._load_vectors()
    word = "test"
    embedding = retrieval_model._embeddings(word)
    
    assert embedding.shape == (300,)
    assert np.array_equal(embedding, np.array([1.0] * 300))

def test_compute_vectors_dict(retrieval_model):
    records_dictionary = {
        "1": {"itunes_url": "url1", "average_rating": 4.5, "text": "test text"}
    }
    retrieval_model.compute_vectors_dict(records_dictionary)
    
    assert "1" in retrieval_model.vectors_dict
    assert retrieval_model.vectors_dict["1"]["itunes_url"] == "url1"
    assert retrieval_model.vectors_dict["1"]["average_rating"] == 4.5
    assert retrieval_model.vectors_dict["1"]["average_vector"].shape == (300,)

def test_get_similarity(retrieval_model):
    query_embedding = np.array([1.0] * 300)
    average_vec = np.array([1.0] * 300)
    similarity = retrieval_model._get_similarity(query_embedding, average_vec)
    assert similarity[0] == 1 - 0.1

def test_rankings_no_boost(retrieval_model):
    retrieval_model._load_vectors()
    retrieval_model.vectors_dict = {
        "1": {"itunes_url": "url1", "average_rating": 4.5, "average_vector": np.array([1.0] * 300)}
    }
    ranks = retrieval_model.rankings(query="test", top_n=1, boost_mode=False)
    assert len(ranks) == 1
    assert ranks[0][0] == "url1"
    assert ranks[0][1] == [1 - 0.1]

def test_rankings_with_boost(retrieval_model):
    retrieval_model._load_vectors()
    retrieval_model.vectors_dict = {
        "1": {"itunes_url": "url1", "average_rating": 4.5, "average_vector": np.array([1.0] * 300)}
    }
    ranks = retrieval_model.rankings(query="test", top_n=1, boost_mode=True)
    assert len(ranks) == 1
    assert ranks[0][0] == "url1"
    assert ranks[0][1] == (1 - 0.1) * 4.5
