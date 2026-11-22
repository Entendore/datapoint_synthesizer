"""
NLP format generators
"""

import re
from typing import Dict, List


class NLPFormatGenerator:
    """Generates NLP data formats."""
    
    def generate_ner_bio(self, text: str) -> Dict:
        """Generates BIO-tagged NER data."""
        tokens = text.split()
        tags = []
        
        for token in tokens:
            if token[0].isupper() and len(token) > 2:
                tags.append("B-ENTITY")
            else:
                tags.append("O")
        
        return {
            "format": "ner_bio",
            "tokens": tokens,
            "tags": tags,
            "sentence": text
        }
    
    def generate_classification(self, text: str, label: str = None) -> Dict:
        """Generates classification data."""
        if label is None:
            label = self._infer_label(text)
        
        return {
            "format": "classification",
            "text": text,
            "label": label,
            "confidence": 0.85
        }
    
    def generate_summarization(self, text: str, ratio: float = 0.3) -> Dict:
        """Generates extractive summarization data."""
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
        
        n_summary = max(1, int(len(sentences) * ratio))
        summary = '. '.join(sentences[:n_summary]) + '.'
        
        return {
            "format": "summarization",
            "original": text,
            "summary": summary,
            "compression_ratio": len(summary) / max(1, len(text))
        }
    
    def _infer_label(self, text: str) -> str:
        text_lower = text.lower()
        
        tech_keywords = ['code', 'api', 'algorithm', 'python', 'data', 'neural']
        legal_keywords = ['law', 'court', 'act', 'legal', 'regulation']
        medical_keywords = ['health', 'medical', 'disease', 'treatment', 'patient']
        
        tech_score = sum(1 for w in tech_keywords if w in text_lower)
        legal_score = sum(1 for w in legal_keywords if w in text_lower)
        medical_score = sum(1 for w in medical_keywords if w in text_lower)
        
        scores = {'tech': tech_score, 'legal': legal_score, 'medical': medical_score}
        max_score = max(scores.values())
        
        if max_score == 0:
            return 'general'
        return max(scores, key=scores.get)
