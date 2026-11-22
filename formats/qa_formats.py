"""
QA format generators - MCQ, T/F, multi-hop
"""

import random
import re
from typing import Dict, List, Optional


class QAFormatGenerator:
    """Generates QA data formats."""
    
    def generate_mcq(self, question: str, correct: str, 
                    distractors: List[str]) -> Optional[Dict]:
        """Generates multiple choice question."""
        if len(distractors) < 3:
            return None
        
        distractors = distractors[:3]
        options = distractors + [correct]
        random.shuffle(options)
        
        options_dict = {chr(65+i): opt for i, opt in enumerate(options)}
        correct_letter = [k for k, v in options_dict.items() if v == correct][0]
        
        return {
            "format": "multiple_choice",
            "question": question,
            "options": options_dict,
            "correct_answer": correct_letter,
            "correct_text": correct,
            "generation_method": "template"
        }
    
    def generate_true_false(self, statement: str, is_true: bool) -> Dict:
        """Generates true/false question."""
        return {
            "format": "true_false",
            "question": statement,
            "correct_answer": is_true,
            "explanation": "Consistent with source." if is_true else "Contradicts source."
        }
    
    def generate_wh_question(self, entity: str, entity_type: str,
                            context: str) -> Dict:
        """Generates wh-question."""
        wh_map = {
            "PERSON": "Who",
            "GPE": "Where",
            "LOC": "Where",
            "DATE": "When",
            "ORG": "Which organization"
        }
        
        wh_word = wh_map.get(entity_type, "What")
        question = f"{wh_word} is related to {entity} in the context?"
        
        return {
            "format": "wh_question",
            "question": question,
            "answer": entity,
            "answer_type": entity_type,
            "context": context
        }
