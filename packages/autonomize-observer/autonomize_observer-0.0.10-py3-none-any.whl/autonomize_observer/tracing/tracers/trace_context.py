"""
Trace context management for streaming traces.

This module provides the StreamingTraceContext class for managing
trace state in a thread-safe manner.
"""

import threading
import time
from typing import Any, Dict, List, Optional


class StreamingTraceContext:
    """Context for managing streaming trace state."""

    def __init__(
        self,
        trace_id: str,
        flow_id: str,
        trace_name: str,
        project_name: str,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
    ):
        self.trace_id = trace_id
        self.flow_id = flow_id
        self.trace_name = trace_name
        self.project_name = project_name
        self.user_id = user_id
        self.session_id = session_id

        # Tracking state
        self.start_time = time.time()
        self.active_spans: Dict[str, Dict[str, Any]] = {}
        self.completed_spans: List[str] = []

        # Thread safety
        self._lock = threading.Lock()

        # Metadata
        self.tags: Dict[str, str] = {}
        self.params: Dict[str, Any] = {}
        self.metrics: Dict[str, float] = {}

    def add_span(self, span_id: str, span_info: Dict[str, Any]) -> None:
        """Add an active span to the context."""
        with self._lock:
            self.active_spans[span_id] = span_info

    def complete_span(self, span_id: str) -> Optional[Dict[str, Any]]:
        """Mark a span as completed and return its info."""
        with self._lock:
            span_info = self.active_spans.pop(span_id, None)
            if span_info:
                self.completed_spans.append(span_id)
            return span_info

    def update_tags(self, tags: Dict[str, str]) -> None:
        """Update trace tags."""
        self.tags.update(tags)

    def set_param(self, key: str, value: Any) -> None:
        """Set a parameter."""
        self.params[key] = value

    def set_metric(self, key: str, value: float) -> None:
        """Set a metric."""
        self.metrics[key] = value

    def get_span_count(self) -> int:
        """Get the total number of completed spans."""
        with self._lock:
            return len(self.completed_spans)
