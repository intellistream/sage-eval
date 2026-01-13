"""BLEU score metric for text generation."""

from __future__ import annotations

import math
from collections import Counter
from dataclasses import dataclass, field
from typing import Any

# Try importing SAGE base class
try:
    from sage.libs.eval.interface.base import BaseMetric, MetricType

    _HAS_SAGE = True
except ImportError:
    BaseMetric = object
    MetricType = None
    _HAS_SAGE = False


@dataclass
class MetricResult:
    """Result from metric computation."""

    name: str
    score: float
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def value(self) -> float:
        """Alias for score to match SAGE interface."""
        return self.score


class BLEUMetric(BaseMetric):
    """BLEU (Bilingual Evaluation Understudy) metric.

    Computes BLEU score for machine translation and text generation.
    Uses smoothed n-gram precision with brevity penalty.

    Example:
        >>> metric = BLEUMetric()
        >>> predictions = ["the cat sat on the mat"]
        >>> references = ["the cat is on the mat"]
        >>> result = metric.compute(predictions, references)
        >>> print(f"BLEU: {result.score:.4f}")
    """

    def __init__(
        self,
        name: str = "bleu",
        max_n: int = 4,
        smoothing: bool = True,
    ) -> None:
        """Initialize BLEU metric.

        Args:
            name: Name of this metric instance.
            max_n: Maximum n-gram order (default 4 for BLEU-4).
            smoothing: Whether to apply smoothing to avoid zero scores.
        """
        self._name = name
        self._max_n = max_n
        self._smoothing = smoothing

    @property
    def name(self) -> str:
        """Return metric name."""
        return self._name

    @property
    def metric_type(self) -> Any:
        """Return metric type."""
        if _HAS_SAGE and MetricType is not None:
            return MetricType.BLEU
        return "bleu"

    def compute(
        self,
        predictions: list[str],
        references: list[str | list[str]],
        **kwargs: Any,
    ) -> MetricResult:
        """Compute BLEU score.

        Args:
            predictions: List of candidate translations/outputs.
            references: List of reference translations. Can be single string
                       or list of multiple references per example.
            **kwargs: Additional parameters (unused).

        Returns:
            MetricResult with BLEU score.
        """
        if len(predictions) != len(references):
            raise ValueError(
                f"Length mismatch: {len(predictions)} predictions vs {len(references)} references"
            )

        if len(predictions) == 0:
            return MetricResult(
                name=self._name,
                score=0.0,
                metadata={"warning": "Empty input"},
            )

        total_matches = [0] * self._max_n
        total_counts = [0] * self._max_n
        total_cand_len = 0
        total_ref_len = 0

        for cand, ref in zip(predictions, references, strict=True):
            # Normalize references
            if isinstance(ref, str):
                refs = [ref]
            else:
                refs = ref

            cand_tokens = cand.lower().split()
            ref_tokens_list = [r.lower().split() for r in refs]

            # Choose closest reference length
            closest_ref_len = min(
                (abs(len(r) - len(cand_tokens)), len(r)) for r in ref_tokens_list
            )[1]

            total_cand_len += len(cand_tokens)
            total_ref_len += closest_ref_len

            # Count n-gram matches
            for n in range(1, self._max_n + 1):
                cand_ngrams = self._get_ngrams(cand_tokens, n)

                # Merge reference n-grams (max count)
                max_ref_ngrams: Counter[tuple[str, ...]] = Counter()
                for ref_tokens in ref_tokens_list:
                    ref_ngrams = self._get_ngrams(ref_tokens, n)
                    for ng, count in ref_ngrams.items():
                        max_ref_ngrams[ng] = max(max_ref_ngrams[ng], count)

                # Clipped matches
                matches = sum(min(count, max_ref_ngrams[ng]) for ng, count in cand_ngrams.items())

                total_matches[n - 1] += matches
                total_counts[n - 1] += sum(cand_ngrams.values())

        # Compute precisions
        precisions = []
        for n in range(self._max_n):
            if total_counts[n] == 0:
                precisions.append(0.0)
            elif total_matches[n] == 0:
                if self._smoothing:
                    precisions.append(1.0 / (total_counts[n] + 1))
                else:
                    precisions.append(0.0)
            else:
                precisions.append(total_matches[n] / total_counts[n])

        # Check for zero precisions
        if any(p == 0 for p in precisions):
            return MetricResult(
                name=self._name,
                score=0.0,
                metadata={
                    "precisions": precisions,
                    "brevity_penalty": 0.0,
                    "candidate_length": total_cand_len,
                    "reference_length": total_ref_len,
                },
            )

        # Geometric mean of precisions
        log_precision = sum(math.log(p) for p in precisions) / self._max_n

        # Brevity penalty
        if total_cand_len <= total_ref_len:
            bp = math.exp(1 - total_ref_len / total_cand_len) if total_cand_len > 0 else 0.0
        else:
            bp = 1.0

        bleu = bp * math.exp(log_precision)

        return MetricResult(
            name=self._name,
            score=bleu,
            metadata={
                "precisions": precisions,
                "brevity_penalty": bp,
                "candidate_length": total_cand_len,
                "reference_length": total_ref_len,
            },
        )

    @staticmethod
    def _get_ngrams(tokens: list[str], n: int) -> Counter[tuple[str, ...]]:
        """Extract n-grams from token list.

        Args:
            tokens: List of tokens.
            n: N-gram order.

        Returns:
            Counter of n-gram tuples.
        """
        ngrams: list[tuple[str, ...]] = []
        for i in range(len(tokens) - n + 1):
            ngrams.append(tuple(tokens[i : i + n]))
        return Counter(ngrams)
