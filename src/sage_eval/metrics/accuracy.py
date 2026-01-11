"""Accuracy metric for classification tasks."""

from __future__ import annotations

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

    # For SAGE compatibility
    @property
    def value(self) -> float:
        """Alias for score to match SAGE interface."""
        return self.score


class AccuracyMetric(BaseMetric):
    """Accuracy metric for classification.

    Computes the proportion of correct predictions out of all predictions.
    Supports both single-label and top-k accuracy.

    Example:
        >>> metric = AccuracyMetric()
        >>> predictions = [1, 0, 1, 1]
        >>> references = [1, 0, 0, 1]
        >>> result = metric.compute(predictions, references)
        >>> print(f"Accuracy: {result.score:.2%}")  # 75.00%
    """

    def __init__(
        self,
        name: str = "accuracy",
        top_k: int = 1,
        normalize: bool = True,
    ) -> None:
        """Initialize accuracy metric.

        Args:
            name: Name of this metric instance.
            top_k: Consider prediction correct if true label is in top-k.
            normalize: If True, return proportion. If False, return count.
        """
        self._name = name
        self._top_k = top_k
        self._normalize = normalize

    @property
    def name(self) -> str:
        """Return metric name."""
        return self._name

    @property
    def metric_type(self) -> Any:
        """Return metric type."""
        if _HAS_SAGE and MetricType is not None:
            return MetricType.ACCURACY
        return "accuracy"

    def compute(
        self,
        predictions: list[Any],
        references: list[Any],
        **kwargs: Any,
    ) -> MetricResult:
        """Compute accuracy score.

        Args:
            predictions: Model predictions. For top-k, should be lists of predictions.
            references: Ground truth labels.
            **kwargs: Additional parameters:
                - top_k: Override the top_k setting
                - normalize: Override the normalize setting

        Returns:
            MetricResult with accuracy score.

        Raises:
            ValueError: If inputs are empty or have mismatched lengths.
        """
        if len(predictions) != len(references):
            raise ValueError(
                f"Length mismatch: {len(predictions)} predictions vs {len(references)} references"
            )

        if len(predictions) == 0:
            raise ValueError("Cannot compute accuracy on empty inputs")

        top_k = kwargs.get("top_k", self._top_k)
        normalize = kwargs.get("normalize", self._normalize)

        if top_k == 1:
            # Standard accuracy
            correct = sum(1 for p, r in zip(predictions, references, strict=True) if p == r)
        else:
            # Top-k accuracy
            correct = sum(
                1
                for preds, ref in zip(predictions, references, strict=True)
                if ref in preds[:top_k]
            )

        accuracy = correct / len(predictions) if normalize else correct

        return MetricResult(
            name=self._name,
            score=accuracy,
            metadata={
                "correct": correct,
                "total": len(predictions),
                "top_k": top_k,
                "normalized": normalize,
            },
        )

    def compute_per_class(
        self,
        predictions: list[Any],
        references: list[Any],
    ) -> dict[Any, float]:
        """Compute per-class accuracy.

        Args:
            predictions: Model predictions.
            references: Ground truth labels.

        Returns:
            Dictionary mapping class labels to their accuracy.
        """
        classes: dict[Any, dict[str, int]] = {}

        for pred, ref in zip(predictions, references, strict=True):
            if ref not in classes:
                classes[ref] = {"correct": 0, "total": 0}
            classes[ref]["total"] += 1
            if pred == ref:
                classes[ref]["correct"] += 1

        return {
            cls: stats["correct"] / stats["total"] if stats["total"] > 0 else 0.0
            for cls, stats in classes.items()
        }
