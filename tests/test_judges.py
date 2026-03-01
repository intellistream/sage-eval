"""Tests for LLM judges."""

import pytest

from sage_libs.sage_eval.judges import FaithfulnessJudge, RelevanceJudge


class TestFaithfulnessJudge:
    """Tests for FaithfulnessJudge."""

    def test_name(self):
        """Test judge name."""
        judge = FaithfulnessJudge(name="test_faithfulness")
        assert judge.name == "test_faithfulness"

    def test_criteria(self):
        """Test judge criteria."""
        judge = FaithfulnessJudge()
        assert judge.criteria == "faithfulness"

    def test_judge_without_llm_raises(self):
        """Test that judge without LLM function raises error."""
        judge = FaithfulnessJudge()
        with pytest.raises(RuntimeError, match="LLM function not set"):
            judge.judge(
                response="Test response",
                context="Test context",
                question="Test question",
            )

    def test_set_llm_fn(self):
        """Test setting LLM function."""

        def mock_llm(prompt: str) -> str:
            return "SCORE: 0.8\nREASONING: Good faithfulness."

        judge = FaithfulnessJudge()
        judge.set_llm_fn(mock_llm)

        result = judge.judge(
            response="Paris is the capital.",
            context="France's capital is Paris.",
            question="What is the capital of France?",
        )

        assert result.score == 0.8
        assert "Good faithfulness" in result.reasoning

    def test_judge_with_constructor_llm(self):
        """Test judge with LLM function in constructor."""

        def mock_llm(prompt: str) -> str:
            return "SCORE: 1.0\nREASONING: Perfectly faithful."

        judge = FaithfulnessJudge(llm_fn=mock_llm)
        result = judge.judge(
            response="Test response",
            context="Test context",
            question="Test question",
        )

        assert result.score == 1.0

    def test_parse_response_with_reasoning(self):
        """Test parsing response with multi-line reasoning."""

        def mock_llm(prompt: str) -> str:
            return """SCORE: 0.75
REASONING: The response is mostly faithful.
However, it adds some minor interpretations.
Overall acceptable."""

        judge = FaithfulnessJudge(llm_fn=mock_llm)
        result = judge.judge(
            response="Test",
            context="Context",
            question="Question",
        )

        assert result.score == 0.75
        assert "mostly faithful" in result.reasoning

    def test_score_out_of_range_raises(self):
        """Test that out-of-range score raises ValueError."""

        def mock_llm(prompt: str) -> str:
            return "SCORE: 1.5\nREASONING: Over the top"

        judge = FaithfulnessJudge(llm_fn=mock_llm)
        with pytest.raises(ValueError, match="SCORE must be between 0.0 and 1.0"):
            judge.judge(
                response="Test",
                context="Context",
                question="Question",
            )

    def test_missing_score_raises(self):
        """Test that missing SCORE field raises ValueError."""

        def mock_llm(prompt: str) -> str:
            return "REASONING: only reasoning"

        judge = FaithfulnessJudge(llm_fn=mock_llm)
        with pytest.raises(ValueError, match="Missing SCORE field"):
            judge.judge(
                response="Test",
                context="Context",
                question="Question",
            )

    def test_missing_reasoning_raises(self):
        """Test that missing REASONING field raises ValueError."""

        def mock_llm(prompt: str) -> str:
            return "SCORE: 0.8"

        judge = FaithfulnessJudge(llm_fn=mock_llm)
        with pytest.raises(ValueError, match="Missing REASONING field"):
            judge.judge(
                response="Test",
                context="Context",
                question="Question",
            )

    def test_with_reference(self):
        """Test judge with reference answer."""

        def mock_llm(prompt: str) -> str:
            assert "Reference answer" in prompt
            return "SCORE: 0.9\nREASONING: Close to reference."

        judge = FaithfulnessJudge(llm_fn=mock_llm)
        result = judge.judge(
            response="Test response",
            context="Test context",
            question="Test question",
            reference="Reference answer",
        )

        assert result.score == 0.9


class TestRelevanceJudge:
    """Tests for RelevanceJudge."""

    def test_name(self):
        """Test judge name."""
        judge = RelevanceJudge(name="test_relevance")
        assert judge.name == "test_relevance"

    def test_criteria(self):
        """Test judge criteria."""
        judge = RelevanceJudge()
        assert judge.criteria == "relevance"

    def test_judge_without_llm_raises(self):
        """Test that judge without LLM function raises error."""
        judge = RelevanceJudge()
        with pytest.raises(RuntimeError, match="LLM function not set"):
            judge.judge(
                response="Test response",
                question="Test question",
            )

    def test_judge_without_question_raises(self):
        """Test that judge without question raises error."""

        def mock_llm(prompt: str) -> str:
            return "SCORE: 0.5\nREASONING: Test"

        judge = RelevanceJudge(llm_fn=mock_llm)
        with pytest.raises(ValueError, match="Question is required"):
            judge.judge(response="Test response")

    def test_basic_relevance(self):
        """Test basic relevance judgment."""

        def mock_llm(prompt: str) -> str:
            return "SCORE: 0.9\nREASONING: Highly relevant response."

        judge = RelevanceJudge(llm_fn=mock_llm)
        result = judge.judge(
            response="Paris is the capital of France.",
            question="What is the capital of France?",
        )

        assert result.score == 0.9
        assert "relevant" in result.reasoning.lower()

    def test_with_context(self):
        """Test relevance judgment with context."""

        def mock_llm(prompt: str) -> str:
            assert "Context" in prompt
            return "SCORE: 0.8\nREASONING: Uses context well."

        judge = RelevanceJudge(llm_fn=mock_llm)
        result = judge.judge(
            response="Test response",
            context="Relevant context here",
            question="Test question",
        )

        assert result.score == 0.8

    def test_metadata_includes_lengths(self):
        """Test that metadata includes length information."""

        def mock_llm(prompt: str) -> str:
            return "SCORE: 0.7\nREASONING: OK"

        judge = RelevanceJudge(llm_fn=mock_llm)
        result = judge.judge(
            response="Short response",
            question="What is the question?",
        )

        assert "response_length" in result.metadata
        assert "question_length" in result.metadata
        assert result.metadata["response_length"] == len("Short response")
