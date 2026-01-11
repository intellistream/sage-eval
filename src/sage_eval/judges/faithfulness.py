"""Faithfulness judge for evaluating response fidelity to context."""

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


class FaithfulnessJudge(BaseLLMJudge):
    """Judge for evaluating faithfulness of responses to provided context.

    Faithfulness measures whether the response only contains information
    that can be verified from the provided context (no hallucinations).

    Example:
        >>> judge = FaithfulnessJudge(llm_fn=my_llm_call)
        >>> result = judge.judge(
        ...     response="Paris is the capital of France.",
        ...     context="France is a country in Europe. Its capital is Paris.",
        ...     question="What is the capital of France?"
        ... )
        >>> print(f"Faithfulness: {result.score:.2f}")
    """

    PROMPT_TEMPLATE = """You are evaluating the faithfulness of a response.

Faithfulness measures whether ALL claims in the response can be verified from the provided context.
A faithful response contains NO information that cannot be found in or logically derived from the context.

Context:
{context}

Question:
{question}

Response to evaluate:
{response}

{reference_section}

Evaluate the faithfulness of the response on a scale of 0.0 to 1.0:
- 1.0: All claims are supported by the context
- 0.5: Some claims are supported, some cannot be verified
- 0.0: Contains significant unsupported claims (hallucinations)

Provide your evaluation in this exact format:
SCORE: <number between 0.0 and 1.0>
REASONING: <your detailed reasoning>"""

    def __init__(
        self,
        llm_fn: Callable[[str], str] | None = None,
        name: str = "faithfulness",
    ) -> None:
        """Initialize the faithfulness judge.

        Args:
            llm_fn: Function that takes a prompt and returns LLM response.
                   If None, judge() will raise an error.
            name: Name of this judge instance.
        """
        self._name = name
        self._llm_fn = llm_fn
        self._criteria = "faithfulness"

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
        context: str,
        question: str | None = None,
        reference: str | None = None,
    ) -> JudgmentResult:
        """Evaluate faithfulness of a response.

        Args:
            response: The response to evaluate.
            context: The context/source material.
            question: The original question (optional).
            reference: Reference answer (optional, for comparison).

        Returns:
            JudgmentResult with score and reasoning.

        Raises:
            RuntimeError: If llm_fn is not set.
        """
        if self._llm_fn is None:
            raise RuntimeError(
                "LLM function not set. Use set_llm_fn() or pass llm_fn to constructor."
            )

        reference_section = ""
        if reference:
            reference_section = f"\nReference answer (for comparison):\n{reference}"

        prompt = self.PROMPT_TEMPLATE.format(
            context=context,
            question=question or "(No question provided)",
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
                "context_length": len(context),
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
