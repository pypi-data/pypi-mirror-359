"""Tracing module for autonomize observer."""

# Import from reorganized structure
from .tracers import BaseTracer, StreamingTraceContext
from .utils import (
    clean_model_name,
    clean_trace_name,
    estimate_token_usage_fallback,
    extract_actual_model_name_from_response,
    extract_response_text,
    extract_token_usage_from_response,
    guess_provider_from_model,
    infer_component_type,
)

# Import main tracer implementation
try:
    from .tracers import AgentTracer, streaming_trace

    _has_tracer = True
except ImportError:
    _has_tracer = False
    AgentTracer = None
    streaming_trace = None

# Import LangChain callback
try:
    from .callbacks import LANGCHAIN_AVAILABLE, StreamingLangChainCallback

    _has_langchain = True
except ImportError:
    _has_langchain = False
    StreamingLangChainCallback = None
    LANGCHAIN_AVAILABLE = False

# Export list
__all__ = [
    # Core tracers
    "BaseTracer",
    "StreamingTraceContext",
    # Utilities
    "guess_provider_from_model",
    "clean_model_name",
    "infer_component_type",
    "estimate_token_usage_fallback",
    "extract_token_usage_from_response",
    "extract_actual_model_name_from_response",
    "extract_response_text",
    "clean_trace_name",
    # Availability flags
    "LANGCHAIN_AVAILABLE",
]

# Add available components to exports
if _has_tracer:
    __all__.extend(["AgentTracer", "streaming_trace"])

if _has_langchain:
    __all__.extend(["StreamingLangChainCallback"])
