"""
Autonomize Observer SDK for Reliable LLM Observability.

This SDK provides production-ready observability for LLM applications with:
- Enhanced monitor() function for reliable Kafka integration
- Automatic cost tracking and usage metrics  
- Auto-detection of LLM providers (OpenAI, Anthropic, etc.)
- Built-in error handling and fallbacks

Example:
    from autonomize_observer import monitor
    from openai import OpenAI

    client = monitor(OpenAI(), project_name="my-app", user_id="user123")
    response = client.chat.completions.create(...)
"""

# Converters (base interfaces only)
from .converters.base_converter import BaseConverter

# Core components
from .core.exceptions import ModelHubAPIException

# Kafka schemas
from .kafka.schemas import CompleteTrace, LLMCallEvent, SpanInfo
from .monitoring import (
    agent,
    close_kafka_llm_monitor,
    get_kafka_llm_monitor,
    identify,
    initialize,
    monitor,
    tool,
    trace_async,
    trace_sync,
)

# Enhanced Monitoring (production-ready)
from .monitoring.cost_tracking import CostTracker

# Tracing
from .tracing import AgentTracer

# Utilities
from .utils.logger import setup_logger
from .version import __version__

# Modern API removed - use monitor() function for reliability


__all__ = [
    # Version
    "__version__",
    # Core
    "ModelHubAPIException",
    # Kafka schemas
    "CompleteTrace",
    "LLMCallEvent",
    "SpanInfo",
    # Modern API removed - use monitor() instead
    # Enhanced Monitoring - Core function (recommended)
    "monitor",  # ← Use this for reliable LLM monitoring
    "initialize",
    # Enhanced Monitoring - Additional functions
    "agent",
    "tool",
    "trace_async",
    "trace_sync",
    "identify",
    "get_kafka_llm_monitor",
    "close_kafka_llm_monitor",
    # Enhanced Monitoring - Cost tracking
    "CostTracker",
    # Tracing
    "AgentTracer",
    # Utilities
    "setup_logger",
    # Converters (base interfaces only)
    "BaseConverter",
]
