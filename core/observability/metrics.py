from __future__ import annotations

import threading
from collections import defaultdict
from typing import Any


class MetricsCollector:
    """Lightweight in-memory metrics. Thread-safe."""

    def __init__(self):
        self._lock = threading.Lock()
        self._counters: dict[str, int] = defaultdict(int)
        self._gauges: dict[str, float] = {}
        self._histograms: dict[str, list[float]] = defaultdict(list)

    def increment(self, name: str, value: int = 1, tags: dict | None = None) -> None:
        key = self._key(name, tags)
        with self._lock:
            self._counters[key] += value

    def gauge(self, name: str, value: float, tags: dict | None = None) -> None:
        key = self._key(name, tags)
        with self._lock:
            self._gauges[key] = value

    def histogram(self, name: str, value: float, tags: dict | None = None) -> None:
        key = self._key(name, tags)
        with self._lock:
            self._histograms[key].append(value)

    def snapshot(self) -> dict[str, Any]:
        with self._lock:
            hist_summary = {}
            for k, vals in self._histograms.items():
                if vals:
                    sorted_vals = sorted(vals)
                    n = len(sorted_vals)
                    hist_summary[k] = {
                        "count": n,
                        "min": sorted_vals[0],
                        "max": sorted_vals[-1],
                        "mean": sum(sorted_vals) / n,
                        "p50": sorted_vals[n // 2],
                        "p95": sorted_vals[int(n * 0.95)],
                    }
            return {
                "counters": dict(self._counters),
                "gauges": dict(self._gauges),
                "histograms": hist_summary,
            }

    @staticmethod
    def _key(name: str, tags: dict | None) -> str:
        if not tags:
            return name
        tag_str = ",".join(f"{k}={v}" for k, v in sorted(tags.items()))
        return f"{name}{{{tag_str}}}"


# Global singleton
metrics = MetricsCollector()
