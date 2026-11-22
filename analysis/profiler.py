"""
Data profiler - comprehensive statistical analysis
"""

from typing import Dict, List
from collections import defaultdict

import numpy as np


class DataProfiler:
    """Profiles datapoints and generates statistical summaries."""
    
    def __init__(self):
        self.profile: Dict = {}
    
    def profile_data(self, datapoints: List[Dict]) -> Dict:
        if not datapoints:
            return {}
        
        profile = {
            "total_count": len(datapoints),
            "field_types": {},
            "missing_values": {},
            "unique_values": {},
            "statistics": {},
            "distributions": {},
            "outliers": {},
            "correlations": {}
        }
        
        all_fields = set()
        for dp in datapoints:
            all_fields.update(k for k in dp.keys() if not k.startswith('_'))
        
        for field_name in all_fields:
            values = [dp.get(field_name) for dp in datapoints if field_name in dp]
            
            if not values:
                continue
            
            types = [type(v).__name__ for v in values if v is not None]
            profile["field_types"][field_name] = max(set(types), key=types.count) if types else "unknown"
            
            missing = sum(1 for dp in datapoints if field_name not in dp or dp[field_name] is None)
            profile["missing_values"][field_name] = missing / len(datapoints)
            
            unique = len(set(str(v) for v in values if v is not None))
            profile["unique_values"][field_name] = unique
            
            numeric_values = [v for v in values if isinstance(v, (int, float))]
            if numeric_values:
                profile["statistics"][field_name] = {
                    "mean": float(np.mean(numeric_values)),
                    "std": float(np.std(numeric_values)),
                    "min": float(min(numeric_values)),
                    "max": float(max(numeric_values)),
                    "median": float(np.median(numeric_values)),
                    "q1": float(np.percentile(numeric_values, 25)),
                    "q3": float(np.percentile(numeric_values, 75))
                }
                
                q1 = np.percentile(numeric_values, 25)
                q3 = np.percentile(numeric_values, 75)
                iqr = q3 - q1
                lower_bound = q1 - 1.5 * iqr
                upper_bound = q3 + 1.5 * iqr
                
                outliers = [v for v in numeric_values if v < lower_bound or v > upper_bound]
                profile["outliers"][field_name] = {
                    "count": len(outliers),
                    "percentage": len(outliers) / len(numeric_values),
                    "values": outliers[:10]
                }
            
            if profile["field_types"][field_name] in {"str", "bool"}:
                value_counts = defaultdict(int)
                for v in values:
                    if v is not None:
                        value_counts[str(v)] += 1
                profile["distributions"][field_name] = dict(value_counts)
        
        numeric_fields = [f for f in profile["statistics"].keys()]
        if len(numeric_fields) >= 2:
            corr_matrix = {}
            for f1 in numeric_fields:
                corr_matrix[f1] = {}
                for f2 in numeric_fields:
                    values1 = [dp.get(f1) for dp in datapoints if f1 in dp and isinstance(dp.get(f1), (int, float))]
                    values2 = [dp.get(f2) for dp in datapoints if f2 in dp and isinstance(dp.get(f2), (int, float))]
                    
                    if len(values1) == len(values2) and len(values1) > 1:
                        corr = np.corrcoef(values1, values2)[0, 1]
                        if not np.isnan(corr):
                            corr_matrix[f1][f2] = float(corr)
            profile["correlations"] = corr_matrix
        
        self.profile = profile
        return profile
    
    def generate_report(self) -> str:
        if not self.profile:
            return "No profile available"
        
        lines = [
            "=" * 60,
            "DATA PROFILE REPORT",
            "=" * 60,
            "",
            f"Total datapoints: {self.profile['total_count']}",
            "",
            "📊 FIELD STATISTICS:",
        ]
        
        for field_name, stats in self.profile["statistics"].items():
            lines.append(f"\n  {field_name}:")
            lines.append(f"    Mean: {stats['mean']:.3f} ± {stats['std']:.3f}")
            lines.append(f"    Range: [{stats['min']:.3f}, {stats['max']:.3f}]")
            lines.append(f"    Median: {stats['median']:.3f}")
        
        return "\n".join(lines)
