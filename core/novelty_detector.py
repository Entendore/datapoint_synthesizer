"""
Novelty detector - prevents duplicate generation
"""

from typing import Dict, List, Tuple

import numpy as np

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import TruncatedSVD
from sklearn.preprocessing import normalize


class NoveltyDetector:
    """Prevents duplicate generation using semantic embeddings."""
    
    def __init__(self, threshold: float = 0.85):
        self.threshold = threshold
        self.embeddings: List[np.ndarray] = []
        self.datapoints: List[Dict] = []
        self.vectorizer = TfidfVectorizer(
            analyzer='char_wb', ngram_range=(3, 5),
            max_features=5000, sublinear_tf=True
        )
        self.svd = TruncatedSVD(n_components=32, random_state=42)
        self.fitted = False
    
    def fit(self, datapoints: List[Dict]):
        texts = [self._datapoint_to_text(dp) for dp in datapoints]
        if len(texts) < 2:
            return
        
        tfidf = self.vectorizer.fit_transform(texts)
        self.embeddings = normalize(self.svd.fit_transform(tfidf))
        self.datapoints = datapoints
        self.fitted = True
    
    def is_novel(self, datapoint: Dict) -> Tuple[bool, float]:
        if not self.fitted or len(self.embeddings) == 0:
            return True, 0.0
        
        text = self._datapoint_to_text(datapoint)
        vec = normalize(self.svd.transform(self.vectorizer.transform([text])))
        
        similarities = cosine_similarity(vec, self.embeddings)[0]
        max_sim = float(np.max(similarities))
        
        return max_sim < self.threshold, max_sim
    
    def add(self, datapoint: Dict):
        text = self._datapoint_to_text(datapoint)
        
        if not self.fitted:
            self.vectorizer.fit([text])
            vec = normalize(self.svd.fit_transform(self.vectorizer.transform([text])))
            self.fitted = True
        else:
            vec = normalize(self.svd.transform(self.vectorizer.transform([text])))
        
        self.embeddings.append(vec[0])
        self.datapoints.append(datapoint)
    
    def _datapoint_to_text(self, dp: Dict) -> str:
        parts = []
        for k, v in dp.items():
            if k.startswith('_'):
                continue
            if isinstance(v, str):
                parts.append(v)
            elif isinstance(v, (int, float, bool)):
                parts.append(str(v))
            elif isinstance(v, list):
                parts.append(' '.join(str(x) for x in v))
        return ' '.join(parts)
