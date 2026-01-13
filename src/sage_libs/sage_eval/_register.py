"""Auto-registration of sage-eval components with SAGE framework.

This module automatically registers all evaluation components with SAGE
when the package is imported and SAGE is available.
"""

from __future__ import annotations

# Try to register with SAGE framework
try:
    from sage.libs.eval.interface.factory import (
        register_judge,
        register_metric,
        register_profiler,
    )

    # Import implementations
    from .judges import FaithfulnessJudge, RelevanceJudge
    from .metrics import AccuracyMetric, BLEUMetric, F1Metric
    from .profilers import LatencyProfiler, ThroughputProfiler

    # Register metrics
    register_metric("accuracy", AccuracyMetric)
    register_metric("bleu", BLEUMetric)
    register_metric("f1", F1Metric)

    # Register profilers
    register_profiler("latency", LatencyProfiler)
    register_profiler("throughput", ThroughputProfiler)

    # Register judges
    register_judge("faithfulness", FaithfulnessJudge)
    register_judge("relevance", RelevanceJudge)

    _SAGE_REGISTERED = True

except ImportError:
    # SAGE not available, skip registration
    _SAGE_REGISTERED = False


def is_registered() -> bool:
    """Check if components are registered with SAGE.

    Returns:
        True if registered with SAGE framework, False otherwise.
    """
    return _SAGE_REGISTERED
