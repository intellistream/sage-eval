"""Auto-registration of sage-eval components with SAGE framework.

This module registers all evaluation components with SAGE when imported.
"""

from __future__ import annotations

from sage.libs.eval.interface.factory import (
    registered_judges,
    registered_metrics,
    registered_profilers,
    register_judge,
    register_metric,
    register_profiler,
)

from .judges import FaithfulnessJudge, RelevanceJudge
from .metrics import AccuracyMetric, BLEUMetric, F1Metric
from .profilers import LatencyProfiler, ThroughputProfiler

if "accuracy" not in registered_metrics():
    register_metric("accuracy", AccuracyMetric)
if "bleu" not in registered_metrics():
    register_metric("bleu", BLEUMetric)
if "f1" not in registered_metrics():
    register_metric("f1", F1Metric)

if "latency" not in registered_profilers():
    register_profiler("latency", LatencyProfiler)
if "throughput" not in registered_profilers():
    register_profiler("throughput", ThroughputProfiler)

if "faithfulness" not in registered_judges():
    register_judge("faithfulness", FaithfulnessJudge)
if "relevance" not in registered_judges():
    register_judge("relevance", RelevanceJudge)


def is_registered() -> bool:
    """Check registration status.

    Returns:
        Always True after successful module import.
    """
    return True
