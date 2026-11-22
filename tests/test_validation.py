"""
Tests for validation modules
"""

import pytest
from validation.quality_validator import QualityValidator
from core.structure_analyzer import FieldSignature


def test_quality_validator():
    signatures = {
        "question": FieldSignature(name="question", type="string"),
        "answer": FieldSignature(name="answer", type="string"),
        "difficulty": FieldSignature(
            name="difficulty", type="string",
            is_categorical=True,
            enum_values=["easy", "medium", "hard"]
        ),
    }
    
    validator = QualityValidator(signatures)
    
    valid_dp = {"question": "Q?", "answer": "A", "difficulty": "easy"}
    is_valid, issues = validator.validate(valid_dp)
    assert is_valid
    
    invalid_dp = {"question": "Q?", "answer": "A", "difficulty": "invalid"}
    is_valid, issues = validator.validate(invalid_dp)
    assert not is_valid


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
