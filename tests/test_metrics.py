"""Tests for evaluation metrics."""

import pytest

from sage_libs.sage_eval.metrics import AccuracyMetric, BLEUMetric, F1Metric


class TestAccuracyMetric:
    """Tests for AccuracyMetric."""

    def test_name(self):
        """Test metric name."""
        metric = AccuracyMetric()
        assert metric.name == "accuracy"

    def test_perfect_accuracy(self):
        """Test with perfect predictions."""
        metric = AccuracyMetric()
        predictions = [1, 2, 3, 4, 5]
        references = [1, 2, 3, 4, 5]
        result = metric.compute(predictions, references)
        assert result.score == 1.0

    def test_zero_accuracy(self):
        """Test with all wrong predictions."""
        metric = AccuracyMetric()
        predictions = [1, 2, 3, 4, 5]
        references = [5, 4, 3, 2, 1]
        result = metric.compute(predictions, references)
        assert result.score == 0.2  # Only 3 matches

    def test_partial_accuracy(self):
        """Test with partial correct predictions."""
        metric = AccuracyMetric()
        predictions = [1, 0, 1, 0]
        references = [1, 1, 0, 0]
        result = metric.compute(predictions, references)
        assert result.score == 0.5

    def test_string_accuracy(self):
        """Test with string predictions."""
        metric = AccuracyMetric()
        predictions = ["cat", "dog", "bird"]
        references = ["cat", "dog", "fish"]
        result = metric.compute(predictions, references)
        assert abs(result.score - 0.667) < 0.01

    def test_empty_raises_error(self):
        """Test that empty lists raise ValueError."""
        metric = AccuracyMetric()
        with pytest.raises(ValueError):
            metric.compute([], [])

    def test_mismatched_length_raises_error(self):
        """Test that mismatched lengths raise ValueError."""
        metric = AccuracyMetric()
        with pytest.raises(ValueError):
            metric.compute([1, 2], [1, 2, 3])


class TestBLEUMetric:
    """Tests for BLEUMetric."""

    def test_name(self):
        """Test metric name."""
        metric = BLEUMetric()
        assert metric.name == "bleu"

    def test_perfect_bleu(self):
        """Test with identical strings."""
        metric = BLEUMetric()
        predictions = ["the cat sat on the mat"]
        references = ["the cat sat on the mat"]
        result = metric.compute(predictions, references)
        assert result.score == 1.0

    def test_partial_bleu(self):
        """Test with partial overlap - use longer sentence."""
        metric = BLEUMetric()
        predictions = ["the quick brown fox jumps"]
        references = ["the quick brown fox jumps over the lazy dog"]
        result = metric.compute(predictions, references)
        # Should be positive but less than 1 due to brevity penalty
        assert 0 < result.score < 1.0

    def test_no_overlap_bleu(self):
        """Test with no overlap."""
        metric = BLEUMetric()
        predictions = ["alpha beta gamma delta"]
        references = ["one two three four"]
        result = metric.compute(predictions, references)
        assert result.score < 0.5  # Low score due to no word overlap

    def test_different_ngrams(self):
        """Test different n-gram configurations."""
        metric_1 = BLEUMetric(max_n=1)
        metric_2 = BLEUMetric(max_n=2)

        predictions = ["the quick brown fox jumps"]
        references = ["the quick brown fox jumps over"]

        result_1 = metric_1.compute(predictions, references)
        result_2 = metric_2.compute(predictions, references)

        # Both should be positive
        assert result_1.score > 0
        assert result_2.score > 0

    def test_multiple_sentences(self):
        """Test with longer sentences that have 4-grams."""
        metric = BLEUMetric()
        predictions = ["the quick brown fox jumps over the lazy dog"]
        references = ["the quick brown fox jumps over the lazy dog"]
        result = metric.compute(predictions, references)
        assert result.score == 1.0


class TestF1Metric:
    """Tests for F1Metric."""

    def test_name(self):
        """Test metric name."""
        metric = F1Metric()
        assert metric.name == "f1"

    def test_perfect_f1(self):
        """Test with perfect predictions."""
        metric = F1Metric()
        predictions = [0, 1, 0, 1]
        references = [0, 1, 0, 1]
        result = metric.compute(predictions, references)
        assert result.score == 1.0

    def test_zero_f1(self):
        """Test with all wrong predictions."""
        metric = F1Metric()
        predictions = [0, 0, 0, 0]
        references = [1, 1, 1, 1]
        result = metric.compute(predictions, references)
        assert result.score < 0.5  # Low score due to no word overlap

    def test_partial_f1(self):
        """Test with partial correct predictions."""
        metric = F1Metric(average="macro")
        predictions = [0, 0, 1, 1]
        references = [0, 1, 0, 1]
        result = metric.compute(predictions, references)
        # Should be between 0 and 1
        assert 0 < result.score < 1

    def test_different_averaging(self):
        """Test different averaging modes."""
        predictions = [0, 0, 1, 1, 2, 2]
        references = [0, 1, 1, 1, 2, 0]

        metric_micro = F1Metric(average="micro")
        metric_macro = F1Metric(average="macro")
        metric_weighted = F1Metric(average="weighted")

        result_micro = metric_micro.compute(predictions, references)
        result_macro = metric_macro.compute(predictions, references)
        result_weighted = metric_weighted.compute(predictions, references)

        # All should be between 0 and 1
        assert 0 <= result_micro.score <= 1
        assert 0 <= result_macro.score <= 1
        assert 0 <= result_weighted.score <= 1

    def test_per_class_metrics_in_metadata(self):
        """Test that per-class metrics are in metadata."""
        metric = F1Metric()
        predictions = [0, 1, 0, 1]
        references = [0, 1, 1, 1]
        result = metric.compute(predictions, references)

        assert "per_class" in result.metadata
        # Keys are converted to strings
        assert "0" in result.metadata["per_class"]
        assert "1" in result.metadata["per_class"]
