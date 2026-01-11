"""F1 score metric for classification."""

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

    @property
    def value(self) -> float:
        """Alias for score to match SAGE interface."""
        return self.score


class F1Metric(BaseMetric):
    """F1 score metric for classification.

    Computes the harmonic mean of precision and recall.
    Supports micro, macro, and weighted averaging for multiclass.

    Example:
        >>> metric = F1Metric(average="macro")
        >>> predictions = [0, 1, 1, 0, 1]
        >>> references = [0, 1, 0, 0, 1]
        >>> result = metric.compute(predictions, references)
        >>> print(f"F1: {result.score:.4f}")
    """

    def __init__(
        self,
        name: str = "f1",
        average: str = "macro",
    ) -> None:
        """Initialize F1 metric.

        Args:
            name: Name of this metric instance.
            average: Averaging strategy for multiclass:
                - 'micro': Global TP, FP, FN
                - 'macro': Unweighted mean of per-class F1
                - 'weighted': Weighted mean by support
        """
        self._name = name
        self.average = average

    @property
    def name(self) -> str:
        """Return metric name."""
        return self._name

    @property
    def metric_type(self) -> Any:
        """Return metric type."""
        if _HAS_SAGE and MetricType is not None:
            return MetricType.F1_SCORE
        return "f1_score"

    def compute(
        self,
        predictions: list[Any],
        references: list[Any],
        **kwargs: Any,
    ) -> MetricResult:
        """Compute F1 score.

        Args:
            predictions: Model predictions
            references: Ground truth labels
            **kwargs: Additional parameters:
                - average: Override averaging method

        Returns:
            MetricResult with F1 score
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

        average = kwargs.get("average", self.average)

        # Get all unique classes
        classes = sorted(set(references) | set(predictions))

        # Compute per-class metrics
        per_class_metrics = {}
        for cls in classes:
            tp = sum(
                1 for p, r in zip(predictions, references, strict=True) if p == cls and r == cls
            )
            fp = sum(
                1 for p, r in zip(predictions, references, strict=True) if p == cls and r != cls
            )
            fn = sum(
                1 for p, r in zip(predictions, references, strict=True) if p != cls and r == cls
            )

            precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
            recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
            f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0

            per_class_metrics[cls] = {
                "precision": precision,
                "recall": recall,
                "f1": f1,
                "support": sum(1 for r in references if r == cls),
            }

        # Compute overall F1 based on averaging method
        if average == "micro":
            # Global TP, FP, FN
            total_tp = sum(m["f1"] * m["support"] for m in per_class_metrics.values())
            total_support = sum(m["support"] for m in per_class_metrics.values())
            f1_score = total_tp / total_support if total_support > 0 else 0.0
        elif average == "macro":
            # Simple average of per-class F1
            f1_score = sum(m["f1"] for m in per_class_metrics.values()) / len(classes)
        elif average == "weighted":
            # Weighted by support
            total_support = sum(m["support"] for m in per_class_metrics.values())
            f1_score = (
                sum(m["f1"] * m["support"] for m in per_class_metrics.values()) / total_support
                if total_support > 0
                else 0.0
            )
        else:
            raise ValueError(f"Unknown average method: {average}")

        # Compute overall precision and recall
        overall_precision = sum(m["precision"] for m in per_class_metrics.values()) / len(classes)
        overall_recall = sum(m["recall"] for m in per_class_metrics.values()) / len(classes)

        return MetricResult(
            name=self._name,
            score=f1_score,
            metadata={
                "average": average,
                "precision": overall_precision,
                "recall": overall_recall,
                "per_class": {str(k): v for k, v in per_class_metrics.items()},
                "num_classes": len(classes),
            },
        )
