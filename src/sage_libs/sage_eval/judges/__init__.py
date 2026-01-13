"""LLM judges for evaluating generation quality."""

from .faithfulness import FaithfulnessJudge
from .relevance import RelevanceJudge

__all__ = ["FaithfulnessJudge", "RelevanceJudge"]
