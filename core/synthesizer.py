"""
Main synthesizer v3 - integrates all core features
"""

import copy
from typing import Dict, List, Optional
from datetime import datetime

from .structure_analyzer import EnhancedStructureAnalyzer
from .value_generator import EnhancedValueGenerator
from .rule_miner import RuleMiner
from .novelty_detector import NoveltyDetector
from .coherence_engine import SemanticCoherenceEngine
from .constraint_system import ConstraintSystem
from .strategies import Strategy, STRATEGY_TEMPERATURES
from validation.quality_validator import QualityValidator


class DatapointSynthesizerV3:
    """Enhanced datapoint synthesizer with all v3 features."""
    
    def __init__(self, strategy: Strategy = Strategy.BALANCED):
        self.strategy = strategy
        temperature = STRATEGY_TEMPERATURES[strategy]
        
        self.analyzer = EnhancedStructureAnalyzer()
        self.generator = EnhancedValueGenerator(temperature)
        self.coherence_engine = SemanticCoherenceEngine()
        self.constraint_system = ConstraintSystem()
        self.validator: Optional[QualityValidator] = None
        self.rule_miner = RuleMiner()
        self.novelty_detector = NoveltyDetector(threshold=0.85)
        
        self.signatures: Dict = {}
        self.examples: List[Dict] = []
        self.mined_rules: List[Dict] = []
    
    def set_examples(self, examples: List[Dict]):
        if not examples:
            raise ValueError("Need at least one example")
        
        self.examples = examples
        self.signatures = self.analyzer.analyze_multiple(examples)
        self.validator = QualityValidator(self.signatures)
        self.mined_rules = self.rule_miner.mine(examples)
        self.novelty_detector.fit(examples)
        
        print(f"✅ Analyzed {len(examples)} examples")
        print(f"   Found {len(self.signatures)} fields")
        print(f"   Mined {len(self.mined_rules)} rules")
        print(f"   Strategy: {self.strategy.value} (temp={STRATEGY_TEMPERATURES[self.strategy]})")
    
    def synthesize(self, n: int = 10, validate: bool = True,
                  ensure_novelty: bool = True, add_explanations: bool = False,
                  conditions: Dict = None) -> List[Dict]:
        if not self.examples:
            raise ValueError("Must call set_examples() first")
        
        results = []
        attempts = 0
        max_attempts = n * 5
        
        while len(results) < n and attempts < max_attempts:
            attempts += 1
            
            if conditions:
                new_dp = self._generate_with_conditions(conditions)
                if new_dp is None:
                    continue
            else:
                new_dp = self._generate_one()
            
            new_dp = self.coherence_engine.ensure_coherence(new_dp, self.signatures)
            new_dp = self.constraint_system.apply_constraints(new_dp)
            
            violations = self.rule_miner.check_violations(new_dp)
            if violations:
                continue
            
            if ensure_novelty:
                is_novel, similarity = self.novelty_detector.is_novel(new_dp)
                if not is_novel:
                    continue
                new_dp['_novelty_similarity'] = similarity
            
            if validate and self.validator:
                is_valid, issues = self.validator.validate(new_dp)
                if not is_valid:
                    continue
            
            if add_explanations:
                new_dp['explanation'] = self._generate_explanation(new_dp)
            
            new_dp['_synthesis_id'] = f"syn_{len(results)+1:04d}"
            new_dp['_strategy'] = self.strategy.value
            new_dp['_generated_at'] = datetime.utcnow().isoformat() + "Z"
            
            self.novelty_detector.add(new_dp)
            results.append(new_dp)
        
        print(f"✅ Generated {len(results)} datapoints ({attempts} attempts)")
        return results
    
    def _generate_one(self) -> Dict:
        return self._generate_from_example(self.examples[0])
    
    def _generate_from_example(self, example: Dict) -> Dict:
        result = {}
        
        for key, value in example.items():
            if key.startswith('_'):
                continue
            
            sig = self.signatures.get(key)
            if sig:
                result[key] = self.generator.generate(sig, context=result)
            else:
                result[key] = copy.deepcopy(value)
        
        return result
    
    def _generate_with_conditions(self, conditions: Dict, max_attempts: int = 50) -> Optional[Dict]:
        for _ in range(max_attempts):
            dp = self._generate_one()
            
            satisfied = True
            for field_name, target_value in conditions.items():
                if field_name not in dp:
                    satisfied = False
                    break
                
                actual_value = dp[field_name]
                
                if isinstance(target_value, dict):
                    if "min" in target_value and actual_value < target_value["min"]:
                        satisfied = False
                        break
                    if "max" in target_value and actual_value > target_value["max"]:
                        satisfied = False
                        break
                elif isinstance(target_value, list):
                    if actual_value not in target_value:
                        satisfied = False
                        break
                else:
                    if actual_value != target_value:
                        satisfied = False
                        break
            
            if satisfied:
                return dp
        
        return None
    
    def _generate_explanation(self, datapoint: Dict) -> str:
        parts = []
        for field_name, value in datapoint.items():
            if field_name.startswith('_'):
                continue
            if isinstance(value, str):
                parts.append(f"The field '{field_name}' is '{value}'.")
            elif isinstance(value, (int, float)):
                parts.append(f"The field '{field_name}' has value {value}.")
            elif isinstance(value, bool):
                parts.append(f"The field '{field_name}' is {'true' if value else 'false'}.")
        
        return ' '.join(parts) if parts else "Generated datapoint."
    
    def get_structure_report(self) -> str:
        lines = ["=" * 60, "STRUCTURE ANALYSIS REPORT", "=" * 60, ""]
        
        for name, sig in self.signatures.items():
            lines.append(f"📌 {name}")
            lines.append(f"   Type: {sig.type}")
            if sig.is_template:
                lines.append(f"   Template: {sig.template}")
            if sig.is_categorical:
                lines.append(f"   Categorical: {sig.enum_values[:10]}")
            lines.append("")
        
        return "\n".join(lines)
    
    def get_rules_report(self) -> str:
        lines = ["=" * 60, "MINED RULES", "=" * 60, ""]
        
        for i, rule in enumerate(self.mined_rules, 1):
            lines.append(f"Rule {i}: {rule['type']}")
            for k, v in rule.items():
                if k != "type":
                    lines.append(f"   {k}: {v}")
            lines.append("")
        
        return "\n".join(lines)
