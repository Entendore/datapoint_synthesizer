"""
Constraint system for field relationships
"""

from typing import Dict, List, Any
from dataclasses import dataclass, field


@dataclass
class Constraint:
    field1: str
    field2: str
    relation: str
    params: Dict = field(default_factory=dict)


class ConstraintSystem:
    """Manages constraints between fields."""
    
    def __init__(self):
        self.constraints: List[Constraint] = []
    
    def add_constraint(self, field1: str, field2: str, relation: str, **params):
        self.constraints.append(Constraint(field1, field2, relation, params))
    
    def apply_constraints(self, datapoint: Dict) -> Dict:
        for constraint in self.constraints:
            if constraint.field1 in datapoint and constraint.field2 in datapoint:
                val1 = datapoint[constraint.field1]
                val2 = datapoint[constraint.field2]
                
                if constraint.relation == "equals":
                    datapoint[constraint.field2] = val1
                elif constraint.relation == "exclusive":
                    if val1 == val2:
                        datapoint[constraint.field2] = self._get_different_value(val2)
        
        return datapoint
    
    def _get_different_value(self, value: Any) -> Any:
        if isinstance(value, str):
            return value + "_alt"
        elif isinstance(value, (int, float)):
            return value + 1
        elif isinstance(value, bool):
            return not value
        return value
