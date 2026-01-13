"""Throughput profiler for measuring operations per second."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any

# Try importing SAGE base class
try:
    from sage.libs.eval.interface.base import BaseProfiler

    _HAS_SAGE = True
except ImportError:
    BaseProfiler = object
    _HAS_SAGE = False


@dataclass
class ThroughputResult:
    """Result from throughput profiling."""

    operations: int
    elapsed_time: float  # seconds
    throughput: float  # operations per second
    unit: str = "ops/sec"
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "operations": self.operations,
            "elapsed_time": self.elapsed_time,
            "throughput": self.throughput,
            "unit": self.unit,
            "metadata": self.metadata,
        }


class ThroughputProfiler(BaseProfiler):
    """Profiler for measuring throughput (operations per second).

    Tracks the number of operations and time elapsed to compute throughput.

    Example:
        >>> profiler = ThroughputProfiler()
        >>> profiler.start()
        >>> for i in range(100):
        ...     process_item(i)
        ...     profiler.tick()  # Count operation
        >>> result = profiler.stop()
        >>> print(f"Throughput: {result.throughput:.2f} ops/sec")

        >>> # Or with batch counting
        >>> profiler.start()
        >>> process_batch(items)
        >>> profiler.tick(count=len(items))
        >>> result = profiler.stop()
    """

    def __init__(self, name: str = "throughput") -> None:
        """Initialize the throughput profiler.

        Args:
            name: Name of this profiler instance.
        """
        self._name = name
        self._start_time: float | None = None
        self._operations: int = 0
        self._last_result: ThroughputResult | None = None

    @property
    def name(self) -> str:
        """Return profiler name."""
        return self._name

    @property
    def operations(self) -> int:
        """Return current operation count."""
        return self._operations

    @property
    def last_result(self) -> ThroughputResult | None:
        """Return the last profiling result."""
        return self._last_result

    def start(self) -> None:
        """Start profiling and reset counters."""
        self._start_time = time.perf_counter()
        self._operations = 0

    def tick(self, count: int = 1) -> None:
        """Record one or more operations.

        Args:
            count: Number of operations to record (default 1).
        """
        self._operations += count

    def stop(self) -> ThroughputResult:
        """Stop profiling and return result.

        Returns:
            ThroughputResult with throughput information.

        Raises:
            RuntimeError: If start() was not called first.
        """
        if self._start_time is None:
            raise RuntimeError("Profiler was not started. Call start() first.")

        end_time = time.perf_counter()
        elapsed = end_time - self._start_time

        # Avoid division by zero
        throughput = self._operations / elapsed if elapsed > 0 else 0.0

        result = ThroughputResult(
            operations=self._operations,
            elapsed_time=elapsed,
            throughput=throughput,
        )
        self._last_result = result
        self._start_time = None

        return result

    def current_throughput(self) -> float:
        """Get current throughput without stopping.

        Returns:
            Current operations per second.

        Raises:
            RuntimeError: If profiler is not running.
        """
        if self._start_time is None:
            raise RuntimeError("Profiler is not running.")

        elapsed = time.perf_counter() - self._start_time
        return self._operations / elapsed if elapsed > 0 else 0.0

    def __enter__(self) -> ThroughputProfiler:
        """Context manager entry."""
        self.start()
        return self

    def __exit__(self, *args: Any) -> None:
        """Context manager exit."""
        self.stop()
