"""
Rule miner - discovers implicit constraints from examples
"""

from typing import Dict, List
from collections import defaultdict

import numpy as np


class RuleMiner:
    """Discovers implicit rules from example datapoints."""
    
    def __init__(self):
        self.rules: List[Dict] = []
    
    def mine(self, examples: List[Dict]) -> List[Dict]:
        if len(examples) < 2:
            return []
        
        self.rules = []
        self._mine_implications(examples)
        self._mine_cooccurrence(examples)
        self._mine_numeric_constraints(examples)
        self._mine_categorical_deps(examples)
        
        return self.rules
    
    def _mine_implications(self, examples: List[Dict]):
        for field1 in examples[0].keys():
            if field1.startswith('_'):
                continue
            
            value_groups = defaultdict(list)
            for ex in examples:
                if field1 in ex:
                    val = ex[field1]
                    if isinstance(val, (str, int, bool)):
                        value_groups[val].append(ex)
            
            for field2 in examples[0].keys():
                if field2 == field1 or field2.startswith('_'):
                    continue
                
                for val1, group in value_groups.items():
                    if len(group) < 2:
                        continue
                    
                    field2_values = [ex.get(field2) for ex in group if field2 in ex]
                    if not field2_values:
                        continue
                    
                    if len(set(str(v) for v in field2_values)) == 1:
                        self.rules.append({
                            "type": "implication",
                            "if_field": field1,
                            "if_value": val1,
                            "then_field": field2,
                            "then_value": field2_values[0],
                            "confidence": 1.0,
                            "support": len(group)
                        })
    
    def _mine_cooccurrence(self, examples: List[Dict]):
        field_presence = defaultdict(int)
        pair_presence = defaultdict(int)
        
        for ex in examples:
            fields = [k for k in ex.keys() if not k.startswith('_')]
            for f in fields:
                field_presence[f] += 1
            for i, f1 in enumerate(fields):
                for f2 in fields[i+1:]:
                    pair_presence[(f1, f2)] += 1
        
        n = len(examples)
        for (f1, f2), count in pair_presence.items():
            p_both = count / n
            p_f1 = field_presence[f1] / n
            p_f2 = field_presence[f2] / n
            
            if p_both > 0.9 and p_both >= p_f1 * 0.9 and p_both >= p_f2 * 0.9:
                self.rules.append({
                    "type": "cooccurrence",
                    "field1": f1,
                    "field2": f2,
                    "probability": p_both
                })
    
    def _mine_numeric_constraints(self, examples: List[Dict]):
        numeric_fields = defaultdict(list)
        
        for ex in examples:
            for k, v in ex.items():
                if isinstance(v, (int, float)) and not k.startswith('_'):
                    numeric_fields[k].append(v)
        
        for field_name, values in numeric_fields.items():
            if len(values) >= 2:
                min_val, max_val = min(values), max(values)
                mean_val, std_val = np.mean(values), np.std(values)
                
                if all(isinstance(v, int) for v in values):
                    self.rules.append({
                        "type": "integer_range",
                        "field": field_name,
                        "min": int(min_val),
                        "max": int(max_val),
                        "mean": float(mean_val),
                        "std": float(std_val)
                    })
                else:
                    self.rules.append({
                        "type": "float_range",
                        "field": field_name,
                        "min": float(min_val),
                        "max": float(max_val),
                        "mean": float(mean_val),
                        "std": float(std_val)
                    })
    
    def _mine_categorical_deps(self, examples: List[Dict]):
        cat_fields = defaultdict(set)
        
        for ex in examples:
            for k, v in ex.items():
                if isinstance(v, (str, bool)) and not k.startswith('_'):
                    if len(str(v)) < 30:
                        cat_fields[k].add(str(v))
        
        for field_name, values in cat_fields.items():
            if 2 <= len(values) <= 10:
                self.rules.append({
                    "type": "categorical",
                    "field": field_name,
                    "values": list(values)
                })
    
    def check_violations(self, datapoint: Dict) -> List[str]:
        violations = []
        
        for rule in self.rules:
            if rule["type"] == "implication":
                if (rule["if_field"] in datapoint and 
                    datapoint[rule["if_field"]] == rule["if_value"]):
                    if rule["then_field"] in datapoint:
                        if datapoint[rule["then_field"]] != rule["then_value"]:
                            violations.append(
                                f"Rule violation: {rule['if_field']}={rule['if_value']} "
                                f"implies {rule['then_field']}={rule['then_value']}"
                            )
            
            elif rule["type"] in {"integer_range", "float_range"}:
                if rule["field"] in datapoint:
                    val = datapoint[rule["field"]]
                    if isinstance(val, (int, float)):
                        if val < rule["min"] or val > rule["max"]:
                            violations.append(
                                f"Rule violation: {rule['field']}={val} "
                                f"outside [{rule['min']}, {rule['max']}]"
                            )
            
            elif rule["type"] == "categorical":
                if rule["field"] in datapoint:
                    val = str(datapoint[rule["field"]])
                    if val not in rule["values"]:
                        violations.append(
                            f"Rule violation: {rule['field']}={val} "
                            f"not in {rule['values']}"
                        )
        
        return violations
