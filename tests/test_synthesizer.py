"""
Tests for the synthesizer
"""

import pytest
from core.synthesizer import DatapointSynthesizerV3
from core.strategies import Strategy


def test_synthesizer_initialization():
    synth = DatapointSynthesizerV3(strategy=Strategy.BALANCED)
    assert synth.strategy == Strategy.BALANCED


def test_set_examples():
    synth = DatapointSynthesizerV3()
    examples = [
        {"question": "What is 1+1?", "answer": "2", "difficulty": "easy"},
        {"question": "What is 2+2?", "answer": "4", "difficulty": "easy"},
    ]
    synth.set_examples(examples)
    assert len(synth.examples) == 2
    assert len(synth.signatures) > 0


def test_synthesize():
    synth = DatapointSynthesizerV3()
    examples = [
        {"question": "What is the capital of France?", "answer": "Paris", "difficulty": "easy"},
        {"question": "What is the capital of Japan?", "answer": "Tokyo", "difficulty": "medium"},
    ]
    synth.set_examples(examples)
    generated = synth.synthesize(n=5, validate=False, ensure_novelty=False)
    assert len(generated) == 5
    assert all("question" in dp for dp in generated)
    assert all("answer" in dp for dp in generated)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
