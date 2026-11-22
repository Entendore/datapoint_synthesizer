"""
Benchmarking module
"""

from typing import Dict, List
import json
import numpy as np


class BenchmarkManager:
    """Manages benchmarking and evaluation."""
    
    def __init__(self):
        self.baselines: Dict[str, List[Dict]] = {}
        self.metrics_history: List[Dict] = []
    
    def add_baseline(self, name: str, datapoints: List[Dict]):
        self.baselines[name] = datapoints
    
    def compute_metrics(self, datapoints: List[Dict]) -> Dict:
        metrics = {
            "count": len(datapoints),
            "field_coverage": self._compute_field_coverage(datapoints),
            "value_diversity": self._compute_value_diversity(datapoints),
            "completeness": self._compute_completeness(datapoints),
            "uniqueness": self._compute_uniqueness(datapoints)
        }
        
        self.metrics_history.append(metrics)
        return metrics
    
    def _compute_field_coverage(self, datapoints: List[Dict]) -> float:
        if not datapoints:
            return 0.0
        
        all_fields = set()
        for dp in datapoints:
            all_fields.update(k for k in dp.keys() if not k.startswith('_'))
        
        if not all_fields:
            return 0.0
        
        coverages = []
        for field in all_fields:
            count = sum(1 for dp in datapoints if field in dp)
            coverages.append(count / len(datapoints))
        
        return float(np.mean(coverages))
    
    def _compute_value_diversity(self, datapoints: List[Dict]) -> float:
        if not datapoints:
            return 0.0
        
        diversities = []
        for dp in datapoints:
            for key, value in dp.items():
                if isinstance(value, str):
                    words = value.split()
                    if words:
                        diversity = len(set(words)) / len(words)
                        diversities.append(diversity)
        
        return float(np.mean(diversities)) if diversities else 0.0
    
    def _compute_completeness(self, datapoints: List[Dict]) -> float:
        if not datapoints:
            return 0.0
        
        all_fields = set()
        for dp in datapoints:
            all_fields.update(k for k in dp.keys() if not k.startswith('_'))
        
        if not all_fields:
            return 0.0
        
        total_cells = len(datapoints) * len(all_fields)
        filled_cells = sum(1 for dp in datapoints for field in all_fields if field in dp)
        
        return filled_cells / total_cells
    
    def _compute_uniqueness(self, datapoints: List[Dict]) -> float:
        if not datapoints:
            return 0.0
        
        unique_count = len(set(json.dumps(dp, sort_keys=True) for dp in datapoints))
        return unique_count / len(datapoints)
    
    def compare_with_baseline(self, datapoints: List[Dict], baseline_name: str) -> Dict:
        if baseline_name not in self.baselines:
            return {"error": f"Baseline '{baseline_name}' not found"}
        
        baseline = self.baselines[baseline_name]
        
        metrics_generated = self.compute_metrics(datapoints)
        metrics_baseline = self.compute_metrics(baseline)
        
        return {
            "generated": metrics_generated,
            "baseline": metrics_baseline,
        }
