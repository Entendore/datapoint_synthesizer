"""
Enhanced value generator with diversity control
"""

import random
from typing import Dict, List, Any, Optional

import numpy as np

try:
    from nltk.corpus import wordnet
    WORDNET_AVAILABLE = True
except Exception:
    WORDNET_AVAILABLE = False

from .structure_analyzer import FieldSignature


class EnhancedValueGenerator:
    """Enhanced value generator with diversity control."""
    
    DOMAIN_VOCABULARIES = {
        "qa": {
            "entity": ["France", "Japan", "Brazil", "Germany", "Italy", "Spain",
                      "Canada", "Australia", "India", "China"],
            "attribute": ["capital", "population", "language", "currency", "leader"],
            "GPE": ["France", "Japan", "Brazil", "Germany", "Italy"],
            "PERSON": ["John", "Marie", "James", "Anna", "David"],
        },
        "rl": {
            "action": ["move_left", "move_right", "jump", "attack", "defend"],
            "state": ["observation", "position", "velocity"],
        },
        "nlp": {
            "task": ["classification", "ner", "parsing", "translation"],
        },
    }
    
    def __init__(self, temperature: float = 1.0):
        self.temperature = temperature
    
    def generate(self, sig: FieldSignature, context: Dict = None) -> Any:
        if sig.type == "null":
            return None
        if sig.type == "bool":
            return self._generate_bool(sig)
        if sig.type == "int":
            return self._generate_int(sig)
        if sig.type == "float":
            return self._generate_float(sig)
        if sig.type == "string":
            return self._generate_string(sig, context)
        if sig.type == "list":
            return self._generate_list(sig, context)
        if sig.type == "dict":
            return self._generate_dict(sig, context)
        return None
    
    def _generate_bool(self, sig: FieldSignature) -> bool:
        if sig.examples:
            p_true = sum(1 for e in sig.examples if e) / len(sig.examples)
        else:
            p_true = 0.5
        p_true = self._apply_temperature(p_true, 0.5)
        return random.random() < p_true
    
    def _generate_int(self, sig: FieldSignature) -> int:
        if sig.is_categorical and sig.enum_values:
            return random.choice(sig.enum_values)
        mean = sig.stats.get("mean", 0)
        std = max(1, sig.stats.get("std", 1)) * self.temperature
        return int(round(np.random.normal(mean, std)))
    
    def _generate_float(self, sig: FieldSignature) -> float:
        mean = sig.stats.get("mean", 0.0)
        std = max(0.01, sig.stats.get("std", 0.1)) * self.temperature
        value = np.random.normal(mean, std)
        return round(float(value), 3)
    
    def _generate_string(self, sig: FieldSignature, context: Dict = None) -> str:
        domain = sig.domain or "general"
        vocab = self.DOMAIN_VOCABULARIES.get(domain, {})
        
        if sig.is_template and sig.template and sig.slots:
            return self._fill_template(sig, vocab, context)
        
        if sig.is_categorical and sig.enum_values:
            return random.choice(sig.enum_values)
        
        if sig.examples:
            return self._generate_variation(random.choice(sig.examples))
        
        return "generated_value"
    
    def _generate_list(self, sig: FieldSignature, context: Dict = None) -> List:
        target_len = int(sig.stats.get("length", 3))
        length = max(1, int(np.random.normal(target_len, 1 * self.temperature)))
        
        if sig.child_schema:
            return [self._generate_dict_from_schema(sig.child_schema, context)
                    for _ in range(length)]
        else:
            element_sig = FieldSignature(
                name=f"{sig.name}[]",
                type=sig.subtype or "string",
                vocab=sig.vocab,
                enum_values=sig.enum_values,
                is_categorical=sig.is_categorical,
                domain=sig.domain
            )
            return [self.generate(element_sig, context) for _ in range(length)]
    
    def _generate_dict(self, sig: FieldSignature, context: Dict = None) -> Dict:
        return self._generate_dict_from_schema(sig.child_schema or {}, context)
    
    def _generate_dict_from_schema(self, schema: Dict[str, FieldSignature],
                                   context: Dict = None) -> Dict:
        result = {}
        for key, child_sig in schema.items():
            result[key] = self.generate(child_sig, context)
        return result
    
    def _fill_template(self, sig: FieldSignature, vocab: Dict[str, List[str]],
                      context: Dict = None) -> str:
        filled = sig.template
        for slot in sig.slots:
            pool = vocab.get(slot, self._get_general_vocab(slot))
            if pool:
                value = random.choice(pool)
                filled = filled.replace(f"{{{slot}}}", value, 1)
        return filled
    
    def _get_general_vocab(self, slot: str) -> List[str]:
        general = {
            "entity": ["France", "Japan", "Brazil", "Germany"],
            "NP": ["the city", "the country", "the person"],
            "GPE": ["France", "Japan", "Brazil"],
            "PERSON": ["John", "Marie", "James"],
        }
        return general.get(slot, [slot])
    
    def _generate_variation(self, original: str) -> str:
        if not WORDNET_AVAILABLE:
            return original
        
        words = original.split()
        new_words = []
        
        for word in words:
            if len(word) <= 3 or word.lower() in {"the", "a", "an", "is", "of"}:
                new_words.append(word)
                continue
            
            synonym_prob = 0.4 * self.temperature
            if random.random() < synonym_prob:
                try:
                    synsets = wordnet.synsets(word.lower())
                    if synsets:
                        lemmas = synsets[0].lemmas()
                        if len(lemmas) > 1:
                            synonym = random.choice(lemmas[1:]).name().replace('_', ' ')
                            if word.istitle():
                                synonym = synonym.title()
                            new_words.append(synonym)
                        else:
                            new_words.append(word)
                    else:
                        new_words.append(word)
                except Exception:
                    new_words.append(word)
            else:
                new_words.append(word)
        
        return ' '.join(new_words)
    
    def _apply_temperature(self, prob: float, baseline: float) -> float:
        if self.temperature == 1.0:
            return prob
        adjusted = baseline + (prob - baseline) / self.temperature
        return max(0.0, min(1.0, adjusted))
