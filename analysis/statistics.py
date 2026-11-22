"""
Statistical analysis module
"""

from typing import Dict, List

try:
    import scipy.stats as stats
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False


class StatisticalAnalyzer:
    """Performs statistical analysis on datapoints."""
    
    def hypothesis_test(self, datapoints: List[Dict], field1: str, field2: str,
                       test_type: str = "t-test") -> Dict:
        if not SCIPY_AVAILABLE:
            return {"error": "scipy not available"}
        
        values1 = [dp.get(field1) for dp in datapoints if field1 in dp and isinstance(dp.get(field1), (int, float))]
        values2 = [dp.get(field2) for dp in datapoints if field2 in dp and isinstance(dp.get(field2), (int, float))]
        
        if len(values1) < 2 or len(values2) < 2:
            return {"error": "Not enough data"}
        
        if test_type == "t-test":
            stat, p_value = stats.ttest_ind(values1, values2)
        elif test_type == "mann-whitney":
            stat, p_value = stats.mannwhitneyu(values1, values2)
        elif test_type == "ks-test":
            stat, p_value = stats.ks_2samp(values1, values2)
        else:
            return {"error": "Unknown test type"}
        
        return {
            "test": test_type,
            "field1": field1,
            "field2": field2,
            "statistic": float(stat),
            "p_value": float(p_value),
            "significant": p_value < 0.05,
            "interpretation": "Significant difference" if p_value < 0.05 else "No significant difference"
        }
    
    def normality_test(self, datapoints: List[Dict], field: str) -> Dict:
        if not SCIPY_AVAILABLE:
            return {"error": "scipy not available"}
        
        values = [dp.get(field) for dp in datapoints if field in dp and isinstance(dp.get(field), (int, float))]
        
        if len(values) < 8:
            return {"error": "Not enough data"}
        
        stat, p_value = stats.shapiro(values)
        
        return {
            "test": "shapiro-wilk",
            "field": field,
            "statistic": float(stat),
            "p_value": float(p_value),
            "normal": p_value > 0.05,
            "interpretation": "Normally distributed" if p_value > 0.05 else "Not normally distributed"
        }
    
    def correlation_test(self, datapoints: List[Dict], field1: str, field2: str) -> Dict:
        if not SCIPY_AVAILABLE:
            return {"error": "scipy not available"}
        
        values1 = [dp.get(field1) for dp in datapoints if field1 in dp and isinstance(dp.get(field1), (int, float))]
        values2 = [dp.get(field2) for dp in datapoints if field2 in dp and isinstance(dp.get(field2), (int, float))]
        
        if len(values1) != len(values2) or len(values1) < 2:
            return {"error": "Not enough data"}
        
        r, p_value = stats.pearsonr(values1, values2)
        rho, sp_p_value = stats.spearmanr(values1, values2)
        
        return {
            "field1": field1,
            "field2": field2,
            "pearson_r": float(r),
            "pearson_p": float(p_value),
            "spearman_rho": float(rho),
            "spearman_p": float(sp_p_value),
            "significant": p_value < 0.05
        }
