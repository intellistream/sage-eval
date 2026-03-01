"""Contract tests for issue #5: metric/judge external behavior stability."""

from __future__ import annotations

import pytest

from sage_libs.sage_eval.judges import FaithfulnessJudge, RelevanceJudge
from sage_libs.sage_eval.metrics import AccuracyMetric, BLEUMetric, F1Metric


def test_metric_result_contract_includes_value_alias_and_metadata() -> None:
    accuracy = AccuracyMetric()
    result = accuracy.compute([1, 0, 1], [1, 1, 1])

    assert result.name == "accuracy"
    assert result.value == result.score
    assert set(result.metadata.keys()) == {"correct", "total", "top_k", "normalized"}


def test_metric_type_contract_is_stable_enum_values() -> None:
    assert str(AccuracyMetric().metric_type.value) == "accuracy"
    assert str(BLEUMetric().metric_type.value) == "bleu"
    assert str(F1Metric().metric_type.value) == "f1_score"


def test_accuracy_top_k_contract_uses_ranked_candidates() -> None:
    metric = AccuracyMetric(top_k=2)
    predictions = [["b", "a"], ["x", "y"], ["c", "d"]]
    references = ["a", "z", "d"]

    result = metric.compute(predictions, references)
    assert result.score == pytest.approx(2 / 3)
    assert result.metadata["top_k"] == 2


def test_f1_contract_rejects_unknown_average() -> None:
    metric = F1Metric()
    with pytest.raises(ValueError, match="Unknown average method"):
        metric.compute([0, 1], [0, 1], average="invalid-average")


def test_judgment_result_contract_to_dict_shape() -> None:
    judge = FaithfulnessJudge(llm_fn=lambda _: "SCORE: 0.8\nREASONING: ok")
    result = judge.judge(response="r", context="c", question="q")
    serialized = result.to_dict()

    assert set(serialized.keys()) == {"score", "reasoning", "criteria", "metadata"}
    assert serialized["criteria"] == "faithfulness"


def test_faithfulness_parser_contract_fails_when_score_line_absent() -> None:
    judge = FaithfulnessJudge(llm_fn=lambda _: "REASONING: only reasoning")
    with pytest.raises(ValueError, match="Missing SCORE field"):
        _ = judge.judge(response="r", context="c", question="q")


def test_relevance_contract_requires_question_and_llm_fn() -> None:
    relevance = RelevanceJudge()
    with pytest.raises(RuntimeError, match="LLM function not set"):
        relevance.judge(response="r", question="q")

    relevance = RelevanceJudge(llm_fn=lambda _: "SCORE: 0.7\nREASONING: ok")
    with pytest.raises(ValueError, match="Question is required"):
        relevance.judge(response="r", question=None)


def test_relevance_contract_prompt_uses_optional_context_placeholder() -> None:
    captured: dict[str, str] = {}

    def fake_llm(prompt: str) -> str:
        captured["prompt"] = prompt
        return "SCORE: 0.6\nREASONING: partial"

    relevance = RelevanceJudge(llm_fn=fake_llm)
    _ = relevance.judge(response="resp", question="question", context=None)

    assert "(No context provided)" in captured["prompt"]
