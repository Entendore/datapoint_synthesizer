"""
Bias detection module
"""

from typing import Dict, List
from collections import defaultdict


class BiasDetector:
    """Detects biases in generated data."""
    
    def detect_demographic_bias(self, datapoints: List[Dict], field: str) -> Dict:
        if not datapoints:
            return {"error": "No datapoints"}
        
        counts = defaultdict(int)
        for dp in datapoints:
            if field in dp:
                value = str(dp[field]).lower()
                counts[value] += 1
        
        total = sum(counts.values())
        if total == 0:
            return {"error": f"Field '{field}' not found"}
        
        distribution = {k: v / total for k, v in counts.items()}
        
        n_categories = len(distribution)
        expected = 1.0 / n_categories if n_categories > 0 else 0
        parity = 1.0 - sum(abs(v - expected) for v in distribution.values()) / 2
        
        return {
            "field": field,
            "distribution": distribution,
            "parity_score": parity,
            "is_biased": parity < 0.7,
            "recommendation": self._get_recommendation(parity)
        }
    
    def detect_representation_bias(self, datapoints: List[Dict]) -> Dict:
        if not datapoints:
            return {"error": "No datapoints"}
        
        biases = {}
        all_fields = set()
        for dp in datapoints:
            all_fields.update(k for k in dp.keys() if not k.startswith('_'))
        
        for field in all_fields:
            values = [dp.get(field) for dp in datapoints if field in dp and isinstance(dp.get(field), str)]
            
            if len(values) < 10:
                continue
            
            value_counts = defaultdict(int)
            for v in values:
                value_counts[v] += 1
            
            max_count = max(value_counts.values())
            max_ratio = max_count / len(values)
            
            if max_ratio > 0.5:
                biases[field] = {
                    "most_common": max(value_counts, key=value_counts.get),
                    "ratio": max_ratio,
                    "is_biased": True
                }
        
        return {
            "total_fields_analyzed": len(all_fields),
            "biased_fields": len(biases),
            "biases": biases
        }
    
    def _get_recommendation(self, parity: float) -> str:
        if parity >= 0.9:
            return "Excellent balance"
        elif parity >= 0.7:
            return "Good balance"
        elif parity >= 0.5:
            return "Moderate bias detected"
        else:
            return "Strong bias detected"
