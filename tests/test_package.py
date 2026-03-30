"""Tests for package structure and imports."""


class TestPackageImports:
    """Tests for package imports."""

    def test_import_package(self):
        """Test that main package imports correctly."""
        import sage_libs.sage_eval as sage_eval

        assert hasattr(sage_eval, "__version__")
        assert sage_eval.__version__ == "0.0.0.1"

    def test_import_metrics(self):
        """Test importing metrics."""
        from sage_libs.sage_eval import AccuracyMetric, BLEUMetric, F1Metric

        assert AccuracyMetric is not None
        assert BLEUMetric is not None
        assert F1Metric is not None

    def test_import_profilers(self):
        """Test importing profilers."""
        from sage_libs.sage_eval import LatencyProfiler, ThroughputProfiler

        assert LatencyProfiler is not None
        assert ThroughputProfiler is not None

    def test_import_judges(self):
        """Test importing judges."""
        from sage_libs.sage_eval import FaithfulnessJudge, RelevanceJudge

        assert FaithfulnessJudge is not None
        assert RelevanceJudge is not None

    def test_all_exports(self):
        """Test that __all__ contains expected exports."""
        import sage_libs.sage_eval as sage_eval

        expected = {
            "__version__",
            "__author__",
            "__email__",
            "AccuracyMetric",
            "BLEUMetric",
            "F1Metric",
            "LatencyProfiler",
            "ThroughputProfiler",
            "FaithfulnessJudge",
            "RelevanceJudge",
        }

        assert set(sage_eval.__all__) == expected

    def test_subpackage_imports(self):
        """Test importing from subpackages."""
        from sage_libs.sage_eval.metrics import AccuracyMetric

        # All should be importable
        assert AccuracyMetric is not None


class TestRegistration:
    """Tests for SAGE registration."""

    def test_registration_status(self):
        """Test registration status function."""
        from sage_libs.sage_eval._register import is_registered

        # Should return boolean
        result = is_registered()
        assert isinstance(result, bool)

        # In standalone mode (no SAGE), should be False
        # When SAGE is available, should be True
        # Either way, function should work
