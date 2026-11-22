"""
Quality validation module
"""

from typing import Dict, List, Tuple, Any


class QualityValidator:
    """Validates generated datapoints for quality."""
    
    def __init__(self, signatures: Dict):
        self.signatures = signatures
    
    def validate(self, datapoint: Dict) -> Tuple[bool, List[str]]:
        issues = []
        
        for field_name, sig in self.signatures.items():
            if field_name not in datapoint:
                issues.append(f"Missing field: {field_name}")
                continue
            
            value = datapoint[field_name]
            
            if not self._check_type(value, sig.type):
                issues.append(f"Wrong type for {field_name}: expected {sig.type}")
            
            if sig.type in {"int", "float"} and isinstance(value, (int, float)):
                if "min" in sig.stats and value < sig.stats["min"]:
                    issues.append(f"{field_name} below minimum")
                if "max" in sig.stats and value > sig.stats["max"]:
                    issues.append(f"{field_name} above maximum")
            
            if sig.is_categorical and value not in sig.enum_values:
                issues.append(f"{field_name} not in enum")
        
        return len(issues) == 0, issues
    
    def _check_type(self, value: Any, expected_type: str) -> bool:
        type_map = {
            "null": lambda v: v is None,
            "bool": lambda v: isinstance(v, bool),
            "int": lambda v: isinstance(v, int) and not isinstance(v, bool),
            "float": lambda v: isinstance(v, (int, float)) and not isinstance(v, bool),
            "string": lambda v: isinstance(v, str),
            "list": lambda v: isinstance(v, list),
            "dict": lambda v: isinstance(v, dict)
        }
        
        checker = type_map.get(expected_type)
        return checker(value) if checker else True
