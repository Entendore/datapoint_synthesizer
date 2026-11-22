"""
Enhanced structure analyzer - learns from multiple examples
"""

import copy
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from collections import defaultdict

import numpy as np

try:
    import spacy
    nlp = spacy.load("en_core_web_sm")
except Exception:
    nlp = None

try:
    from nltk.tokenize import sent_tokenize
except Exception:
    def sent_tokenize(text):
        import re
        return re.split(r'[.!?]+', text)


@dataclass
class FieldSignature:
    name: str
    type: str
    subtype: Optional[str] = None
    pattern: Optional[str] = None
    template: Optional[str] = None
    slots: List[str] = field(default_factory=list)
    vocab: List[str] = field(default_factory=list)
    stats: Dict[str, float] = field(default_factory=dict)
    enum_values: List[Any] = field(default_factory=list)
    is_categorical: bool = False
    is_template: bool = False
    child_schema: Optional[Dict[str, 'FieldSignature']] = None
    domain: Optional[str] = None
    style_metrics: Dict[str, float] = field(default_factory=dict)
    examples: List[Any] = field(default_factory=list)


class EnhancedStructureAnalyzer:
    """Analyzes multiple examples to infer structure with correlations."""
    
    def __init__(self):
        self.signatures: Dict[str, FieldSignature] = {}
        self.correlation_matrix: Dict[str, Dict[str, float]] = defaultdict(dict)
    
    def analyze_multiple(self, examples: List[Dict]) -> Dict[str, FieldSignature]:
        if not examples:
            raise ValueError("Need at least one example")
        
        all_sigs = [self._analyze_single(ex) for ex in examples]
        self.signatures = self._merge_signatures(all_sigs)
        self._compute_correlations(examples)
        
        return self.signatures
    
    def _analyze_single(self, datapoint: Dict) -> Dict[str, FieldSignature]:
        sigs = {}
        self._analyze_dict(datapoint, "", sigs)
        return sigs
    
    def _analyze_dict(self, data: Dict, prefix: str, sigs: Dict):
        for key, value in data.items():
            full_key = f"{prefix}.{key}" if prefix else key
            sig = self._analyze_value(key, value)
            sigs[full_key] = sig
            
            if isinstance(value, dict):
                sig.child_schema = {}
                self._analyze_dict(value, full_key, sigs)
            elif isinstance(value, list) and value and isinstance(value[0], dict):
                sig.child_schema = {}
                for sub_key, sub_value in value[0].items():
                    sub_sig = self._analyze_value(sub_key, sub_value)
                    sig.child_schema[sub_key] = sub_sig
    
    def _analyze_value(self, name: str, value: Any) -> FieldSignature:
        sig = FieldSignature(name=name, type=self._infer_type(value))
        sig.examples = [value]
        
        if value is None:
            sig.type = "null"
        elif isinstance(value, bool):
            sig.enum_values = [True, False]
            sig.is_categorical = True
        elif isinstance(value, (int, float)):
            sig.stats = {"value": value, "min": value, "max": value, "mean": value, "std": 0}
        elif isinstance(value, str):
            self._analyze_string(sig, value)
            sig.style_metrics = self._compute_style_metrics(value)
        elif isinstance(value, list):
            sig.subtype = self._infer_type(value[0]) if value else "unknown"
            sig.stats = {"length": len(value), "min_length": len(value), "max_length": len(value)}
            if value:
                sig.vocab = [str(v) for v in value[:20]]
        
        return sig
    
    def _merge_signatures(self, all_sigs: List[Dict[str, FieldSignature]]) -> Dict[str, FieldSignature]:
        merged = {}
        
        all_fields = set()
        for sigs in all_sigs:
            all_fields.update(sigs.keys())
        
        for field_name in all_fields:
            field_sigs = [sigs[field_name] for sigs in all_sigs if field_name in sigs]
            
            if not field_sigs:
                continue
            
            merged_sig = copy.deepcopy(field_sigs[0])
            
            for sig in field_sigs[1:]:
                merged_sig.examples.extend(sig.examples)
                
                if sig.type in {"int", "float"}:
                    values = [e for e in merged_sig.examples if isinstance(e, (int, float))]
                    if values:
                        merged_sig.stats = {
                            "min": min(values),
                            "max": max(values),
                            "mean": float(np.mean(values)),
                            "std": float(np.std(values))
                        }
                
                if sig.type == "string":
                    merged_sig.vocab = list(set(merged_sig.vocab + sig.vocab))
                
                if sig.is_categorical:
                    merged_sig.enum_values = list(set(merged_sig.enum_values + sig.enum_values))
            
            merged[field_name] = merged_sig
        
        return merged
    
    def _compute_correlations(self, examples: List[Dict]):
        numeric_fields = defaultdict(list)
        
        for example in examples:
            for key, value in self._flatten_dict(example).items():
                if isinstance(value, (int, float)):
                    numeric_fields[key].append(value)
        
        fields = list(numeric_fields.keys())
        for i, f1 in enumerate(fields):
            for j, f2 in enumerate(fields):
                if i < j and len(numeric_fields[f1]) == len(numeric_fields[f2]):
                    if len(numeric_fields[f1]) >= 2:
                        corr = np.corrcoef(numeric_fields[f1], numeric_fields[f2])[0, 1]
                        if not np.isnan(corr):
                            self.correlation_matrix[f1][f2] = float(corr)
                            self.correlation_matrix[f2][f1] = float(corr)
    
    def _compute_style_metrics(self, text: str) -> Dict[str, float]:
        words = text.split()
        sentences = sent_tokenize(text) if text else []
        
        return {
            "avg_word_length": float(np.mean([len(w) for w in words])) if words else 0,
            "avg_sentence_length": len(words) / len(sentences) if sentences else 0,
            "vocabulary_richness": len(set(words)) / len(words) if words else 0,
        }
    
    def _analyze_string(self, sig: FieldSignature, value: str):
        sig.vocab = [value]
        
        if nlp:
            try:
                doc = nlp(value)
                
                if value.strip().endswith('?'):
                    sig.is_template = True
                    sig.template = self._extract_question_template(doc)
                    sig.slots = self._extract_slots(doc)
            except Exception:
                pass
        
        if value.lower() in {"easy", "medium", "hard"}:
            sig.is_categorical = True
            sig.enum_values = ["easy", "medium", "hard"]
        elif value.lower() in {"true", "false"}:
            sig.is_categorical = True
            sig.enum_values = ["true", "false"]
    
    def _extract_question_template(self, doc) -> str:
        template = doc.text
        for ent in doc.ents:
            template = template.replace(ent.text, f"{{{ent.label_}}}")
        return template
    
    def _extract_slots(self, doc) -> List[str]:
        return [ent.label_ for ent in doc.ents]
    
    def _flatten_dict(self, d: Dict, parent_key: str = '') -> Dict:
        items = {}
        for k, v in d.items():
            new_key = f"{parent_key}.{k}" if parent_key else k
            if isinstance(v, dict):
                items.update(self._flatten_dict(v, new_key))
            else:
                items[new_key] = v
        return items
    
    def _infer_type(self, value: Any) -> str:
        if value is None:
            return "null"
        if isinstance(value, bool):
            return "bool"
        if isinstance(value, int):
            return "int"
        if isinstance(value, float):
            return "float"
        if isinstance(value, str):
            return "string"
        if isinstance(value, list):
            return "list"
        if isinstance(value, dict):
            return "dict"
        return "unknown"
