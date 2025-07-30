"""Tracer implementations module."""

from .base_tracer import BaseTracer
from .trace_context import StreamingTraceContext

try:
    from .agent_tracer import AgentTracer, streaming_trace

    _has_agent_tracer = True
except ImportError:
    _has_agent_tracer = False
    AgentTracer = None
    streaming_trace = None

__all__ = ["BaseTracer", "StreamingTraceContext"]

if _has_agent_tracer:
    __all__.extend(["AgentTracer", "streaming_trace"])
