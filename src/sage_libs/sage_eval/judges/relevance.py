"""Relevance judge for evaluating response relevance to questions."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

# Try importing SAGE base class
try:
    from sage.libs.eval.interface.base import BaseLLMJudge

    _HAS_SAGE = True
except ImportError:
    BaseLLMJudge = object
    _HAS_SAGE = False


@dataclass
class JudgmentResult:
    """Result from LLM judgment."""

    score: float  # 0.0 to 1.0
    reasoning: str
    criteria: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "score": self.score,
            "reasoning": self.reasoning,
            "criteria": self.criteria,
            "metadata": self.metadata,
        }


class RelevanceJudge(BaseLLMJudge):
    """Judge for evaluating relevance of responses to questions.

    Relevance measures whether the response actually addresses the question
    and provides useful information for answering it.

    Example:
        >>> judge = RelevanceJudge(llm_fn=my_llm_call)
        >>> result = judge.judge(
        ...     response="Paris is a beautiful city with many museums.",
        ...     context="France has Paris as its capital.",
        ...     question="What is the capital of France?"
        ... )
        >>> print(f"Relevance: {result.score:.2f}")  # May be low
    """

    PROMPT_TEMPLATE = """You are evaluating the relevance of a response to a question.

Relevance measures whether the response directly addresses the question and provides
information that helps answer it. A relevant response stays on topic and answers
what was actually asked.

Question:
{question}

Context (if provided):
{context}

Response to evaluate:
{response}

{reference_section}

Evaluate the relevance of the response on a scale of 0.0 to 1.0:
- 1.0: Directly and completely addresses the question
- 0.7: Addresses the question but includes some irrelevant information
- 0.5: Partially addresses the question
- 0.3: Tangentially related but doesn't really answer the question
- 0.0: Completely off-topic or doesn't address the question at all

Provide your evaluation in this exact format:
SCORE: <number between 0.0 and 1.0>
REASONING: <your detailed reasoning>"""

    def __init__(
        self,
        llm_fn: Callable[[str], str] | None = None,
        name: str = "relevance",
    ) -> None:
        """Initialize the relevance judge.

        Args:
            llm_fn: Function that takes a prompt and returns LLM response.
                   If None, judge() will raise an error.
            name: Name of this judge instance.
        """
        self._name = name
        self._llm_fn = llm_fn
        self._criteria = "relevance"

    @property
    def name(self) -> str:
        """Return judge name."""
        return self._name

    @property
    def criteria(self) -> str:
        """Return evaluation criteria."""
        return self._criteria

    def set_llm_fn(self, llm_fn: Callable[[str], str]) -> None:
        """Set the LLM function for evaluation.

        Args:
            llm_fn: Function that takes a prompt and returns LLM response.
        """
        self._llm_fn = llm_fn

    def judge(
        self,
        response: str,
        context: str | None = None,
        question: str | None = None,
        reference: str | None = None,
    ) -> JudgmentResult:
        """Evaluate relevance of a response.

        Args:
            response: The response to evaluate.
            context: The context/source material (optional).
            question: The original question.
            reference: Reference answer (optional, for comparison).

        Returns:
            JudgmentResult with score and reasoning.

        Raises:
            RuntimeError: If llm_fn is not set.
            ValueError: If question is not provided.
        """
        if self._llm_fn is None:
            raise RuntimeError(
                "LLM function not set. Use set_llm_fn() or pass llm_fn to constructor."
            )

        if not question:
            raise ValueError("Question is required for relevance evaluation.")

        reference_section = ""
        if reference:
            reference_section = f"\nReference answer (for comparison):\n{reference}"

        prompt = self.PROMPT_TEMPLATE.format(
            context=context or "(No context provided)",
            question=question,
            response=response,
            reference_section=reference_section,
        )

        llm_response = self._llm_fn(prompt)
        score, reasoning = self._parse_response(llm_response)

        return JudgmentResult(
            score=score,
            reasoning=reasoning,
            criteria=self._criteria,
            metadata={
                "response_length": len(response),
                "question_length": len(question),
            },
        )

    def _parse_response(self, llm_response: str) -> tuple[float, str]:
        """Parse LLM response to extract score and reasoning.

        Args:
            llm_response: Raw LLM response.

        Returns:
            Tuple of (score, reasoning).
        """
        lines = llm_response.strip().split("\n")
        score = 0.5  # Default
        reasoning = llm_response  # Default to full response

        for i, line in enumerate(lines):
            if line.upper().startswith("SCORE:"):
                try:
                    score_str = line.split(":", 1)[1].strip()
                    score = float(score_str)
                    score = max(0.0, min(1.0, score))  # Clamp to [0, 1]
                except (ValueError, IndexError):
                    pass
            elif line.upper().startswith("REASONING:"):
                reasoning = line.split(":", 1)[1].strip()
                # Include remaining lines in reasoning
                if i + 1 < len(lines):
                    reasoning += "\n" + "\n".join(lines[i + 1 :])
                break

        return score, reasoning
