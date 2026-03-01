"""Tests for profilers."""

import time

import pytest

from sage_libs.sage_eval.profilers import LatencyProfiler, ThroughputProfiler


class TestLatencyProfiler:
    """Tests for LatencyProfiler."""

    def test_name(self):
        """Test profiler name."""
        profiler = LatencyProfiler(name="test_latency")
        assert profiler.name == "test_latency"

    def test_basic_timing(self):
        """Test basic start/stop timing."""
        profiler = LatencyProfiler()
        profiler.start()
        time.sleep(0.1)
        result = profiler.stop()

        assert result.elapsed_time >= 0.1
        assert result.elapsed_time < 0.2  # Allow some tolerance

    def test_context_manager(self):
        """Test context manager interface."""
        profiler = LatencyProfiler()
        with profiler:
            time.sleep(0.05)

        assert profiler.last_result is not None
        assert profiler.last_result.elapsed_time >= 0.05

    def test_decorator(self):
        """Test decorator interface."""
        profiler = LatencyProfiler()

        @profiler.profile
        def slow_function():
            time.sleep(0.05)
            return "done"

        result = slow_function()
        assert result == "done"
        assert profiler.last_result is not None
        assert profiler.last_result.elapsed_time >= 0.05

    def test_stop_without_start_raises(self):
        """Test that stop without start raises error."""
        profiler = LatencyProfiler()
        with pytest.raises(RuntimeError):
            profiler.stop()

    def test_result_has_timestamps(self):
        """Test that result includes timestamps."""
        profiler = LatencyProfiler()
        profiler.start()
        time.sleep(0.01)
        result = profiler.stop()

        assert result.start_time > 0
        assert result.end_time > result.start_time

    def test_multiple_measurements(self):
        """Test multiple consecutive measurements."""
        profiler = LatencyProfiler()

        profiler.start()
        time.sleep(0.05)
        result1 = profiler.stop()

        profiler.start()
        time.sleep(0.1)
        result2 = profiler.stop()

        assert result2.elapsed_time > result1.elapsed_time


class TestThroughputProfiler:
    """Tests for ThroughputProfiler."""

    def test_name(self):
        """Test profiler name."""
        profiler = ThroughputProfiler(name="test_throughput")
        assert profiler.name == "test_throughput"

    def test_basic_throughput(self):
        """Test basic throughput measurement."""
        profiler = ThroughputProfiler()
        profiler.start()

        for _ in range(100):
            profiler.tick()

        time.sleep(0.1)
        result = profiler.stop()

        assert result.operations == 100
        assert result.throughput > 0
        assert result.elapsed_time >= 0.1

    def test_batch_tick(self):
        """Test batch tick counting."""
        profiler = ThroughputProfiler()
        profiler.start()
        profiler.tick(count=50)
        profiler.tick(count=50)
        result = profiler.stop()

        assert result.operations == 100

    def test_context_manager(self):
        """Test context manager interface."""
        profiler = ThroughputProfiler()

        with profiler:
            for _ in range(10):
                profiler.tick()

        assert profiler.last_result is not None
        assert profiler.last_result.operations == 10

    def test_current_throughput(self):
        """Test getting current throughput without stopping."""
        profiler = ThroughputProfiler()
        profiler.start()

        for _ in range(50):
            profiler.tick()

        time.sleep(0.05)
        current = profiler.current_throughput()

        assert current > 0
        assert profiler.operations == 50  # Still running

    def test_stop_without_start_raises(self):
        """Test that stop without start raises error."""
        profiler = ThroughputProfiler()
        with pytest.raises(RuntimeError):
            profiler.stop()

    def test_current_throughput_not_running_raises(self):
        """Test that current_throughput raises when not running."""
        profiler = ThroughputProfiler()
        with pytest.raises(RuntimeError):
            profiler.current_throughput()

    def test_reset_on_start(self):
        """Test that start resets counters."""
        profiler = ThroughputProfiler()

        profiler.start()
        profiler.tick(count=100)
        profiler.stop()

        profiler.start()  # Should reset
        profiler.tick(count=10)
        result = profiler.stop()

        assert result.operations == 10
