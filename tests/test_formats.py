"""
Tests for format generators
"""

import pytest
from formats.rl_formats import RLFormatGenerator
from formats.nlp_formats import NLPFormatGenerator
from formats.qa_formats import QAFormatGenerator


def test_rl_trajectory():
    gen = RLFormatGenerator()
    sentences = ["First sentence.", "Second sentence.", "Third sentence."]
    traj = gen.generate_trajectory(sentences, "doc1")
    assert "trajectory_id" in traj
    assert "steps" in traj
    assert len(traj["steps"]) == 3


def test_ner_bio():
    gen = NLPFormatGenerator()
    result = gen.generate_ner_bio("John lives in Paris")
    assert "tokens" in result
    assert "tags" in result
    assert len(result["tokens"]) == len(result["tags"])


def test_mcq():
    gen = QAFormatGenerator()
    result = gen.generate_mcq(
        "What is the capital of France?",
        "Paris",
        ["London", "Berlin", "Madrid", "Rome"]
    )
    assert result is not None
    assert "options" in result
    assert len(result["options"]) == 4


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
