"""SAGE Eval - Evaluation metrics, profilers, and LLM judges.

This package provides evaluation tools for SAGE pipelines:
- Metrics: Accuracy, BLEU, F1, etc.
- Profilers: Latency, Throughput measurement
- Judges: LLM-based evaluation (Faithfulness, Relevance)
"""

# Auto-register with SAGE if available
from . import _register as _  # noqa: F401
from ._version import __author__, __email__, __version__

# Judges
from .judges import FaithfulnessJudge, RelevanceJudge

# Metrics
from .metrics import AccuracyMetric, BLEUMetric, F1Metric

# Profilers
from .profilers import LatencyProfiler, ThroughputProfiler

__all__ = [
    # Version info
    "__version__",
    "__author__",
    "__email__",
    # Metrics
    "AccuracyMetric",
    "BLEUMetric",
    "F1Metric",
    # Profilers
    "LatencyProfiler",
    "ThroughputProfiler",
    # Judges
    "FaithfulnessJudge",
    "RelevanceJudge",
]
