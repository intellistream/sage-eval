"""Latency profiler for measuring execution time."""

from __future__ import annotations

import functools
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any, TypeVar

# Try importing SAGE base class
try:
    from sage.libs.eval.interface.base import BaseProfiler

    _HAS_SAGE = True
except ImportError:
    BaseProfiler = object
    _HAS_SAGE = False


F = TypeVar("F", bound=Callable[..., Any])


@dataclass
class LatencyResult:
    """Result from latency profiling."""

    elapsed_time: float  # seconds
    start_time: float
    end_time: float
    unit: str = "seconds"
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "elapsed_time": self.elapsed_time,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "unit": self.unit,
            "metadata": self.metadata,
        }


class LatencyProfiler(BaseProfiler):
    """Profiler for measuring execution latency.

    Supports three modes:
    1. Context manager: with profiler: ...
    2. start/stop: profiler.start(); ...; result = profiler.stop()
    3. Decorator: @profiler.profile

    Example:
        >>> profiler = LatencyProfiler()
        >>> with profiler:
        ...     time.sleep(0.1)
        >>> print(profiler.last_result.elapsed_time)  # ~0.1

        >>> @profiler.profile
        ... def slow_function():
        ...     time.sleep(0.1)
        >>> slow_function()
    """

    def __init__(self, name: str = "latency") -> None:
        """Initialize the latency profiler.

        Args:
            name: Name of this profiler instance.
        """
        self._name = name
        self._start_time: float | None = None
        self._end_time: float | None = None
        self._last_result: LatencyResult | None = None

    @property
    def name(self) -> str:
        """Return profiler name."""
        return self._name

    @property
    def last_result(self) -> LatencyResult | None:
        """Return the last profiling result."""
        return self._last_result

    def start(self) -> None:
        """Start timing."""
        self._start_time = time.perf_counter()
        self._end_time = None

    def stop(self) -> LatencyResult:
        """Stop timing and return result.

        Returns:
            LatencyResult with timing information.

        Raises:
            RuntimeError: If start() was not called first.
        """
        if self._start_time is None:
            raise RuntimeError("Profiler was not started. Call start() first.")

        self._end_time = time.perf_counter()
        elapsed = self._end_time - self._start_time

        result = LatencyResult(
            elapsed_time=elapsed,
            start_time=self._start_time,
            end_time=self._end_time,
        )
        self._last_result = result
        self._start_time = None

        return result

    def profile(self, func: F) -> F:
        """Decorator to profile a function.

        Args:
            func: Function to profile.

        Returns:
            Wrapped function that records timing.
        """

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            self.start()
            try:
                return func(*args, **kwargs)
            finally:
                self.stop()

        return wrapper  # type: ignore[return-value]

    def __enter__(self) -> LatencyProfiler:
        """Context manager entry."""
        self.start()
        return self

    def __exit__(self, *args: Any) -> None:
        """Context manager exit."""
        self.stop()
