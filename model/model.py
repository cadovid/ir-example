import gensim
import nltk
import numpy as np
import re
import scipy


class RetrievalModel():
    
    def __init__(self, vectors_path):
        self.model = None
        self.vectors_path = vectors_path + "/GoogleNews-vectors-negative300.bin.gz"
        nltk.download('stopwords')
        nltk.download('punkt')
        
    def _create_stopwords(self):
        self.stopword_list = nltk.corpus.stopwords.words('english')
        print("Stopwords created")
    
    def _load_vectors(self):
        self.model = gensim.models.KeyedVectors.load_word2vec_format(self.vectors_path, binary=True, limit=500000)
        print("Vectors loaded")
    
    def _data_clean(self, text):
        for index, word in enumerate(text):
            if '-' in word:
                word = word.replace('-', ' ')
                word = word.split()
                text[index] = word
        flattened_list = []
        for item in text:
            if isinstance(item, list):
                flattened_list.extend(item)
            else:
                flattened_list.append(item)
        pattern = r'[^a-zA-Z0-9\s]'
        flattened_list = re.sub(pattern,'',' '.join(flattened_list))
        tokens = [token.strip() for token in flattened_list.split()]
        filtered = [token for token in tokens if token.lower() not in self.stopword_list]
        filtered = ' '.join(filtered)
        return filtered

    def _tokenize_text(self, text):
        return self._data_clean(nltk.word_tokenize(text))
    
    def _embeddings(self, word):
        if word in self.model.key_to_index:
            return self.model.get_vector(word)
        else:
            return np.zeros(300)
    
    def compute_vectors_dict(self, records_dictionary):
        self._create_stopwords()
        self._load_vectors()
        vectors_dict = {}
        for podcast_id, value in records_dictionary.items():
            average_vector = (np.mean(np.array([self._embeddings(x) for x in self._tokenize_text(value["text"]).split()]), axis=0))
            output = {podcast_id : {"itunes_url": value["itunes_url"], "average_rating": value["average_rating"], "average_vector": (average_vector)}}
            vectors_dict.update(output)
        self.vectors_dict = vectors_dict
        print("Internal vectors dictionary created")
    
    def _get_similarity(self, query_embedding, average_vec):
        sim = [(1 - scipy.spatial.distance.cosine(query_embedding, average_vec))]
        return sim
    
    def rankings(self, query, top_n, boost_mode):
        query_words = (np.mean(np.array([self._embeddings(x) for x in nltk.word_tokenize(query.lower())], dtype=float), axis=0))
        rank = []
        if not boost_mode:
            for k, v in self.vectors_dict.items():
                rank.append((v["itunes_url"], self._get_similarity(query_words, v["average_vector"])))
        else:
            for k, v in self.vectors_dict.items():
                rank.append((   v["itunes_url"], self._get_similarity(query_words, v["average_vector"])[0] * v["average_rating"] ))
        rank = sorted(rank, key=lambda t: t[1], reverse=True)
        return rank[:top_n]
