"""
Autonomize Observer SDK for ML Observability.

This SDK provides observability capabilities for machine learning workloads
including tracing, monitoring, and analytics.
"""

from .version import __version__

# Core components
from .core.exceptions import ModelHubAPIException

# Kafka schemas
from .kafka.schemas import CompleteTrace, LLMCallEvent, SpanInfo

# Tracing
from .tracing.agent_tracer import AgentTracer

# New Modern API (recommended)
from .core.observer import observe, workflow, step

# Legacy Monitoring (backward compatibility)
from .monitoring.cost_tracking import CostTracker
from .monitoring import (
    # Core functions used in notebooks
    monitor,
    initialize,
    # Decorators
    agent,
    tool,
    trace_async,
    trace_sync,
    # Utility functions
    identify,
    # Kafka monitoring
    get_kafka_llm_monitor,
    close_kafka_llm_monitor,
)

# Utilities
from .utils.logger import setup_logger

# Converters (base interfaces only)
from .converters.base_converter import BaseConverter

__all__ = [
    # Version
    "__version__",
    # Core
    "ModelHubAPIException",
    # Kafka schemas
    "CompleteTrace",
    "LLMCallEvent",
    "SpanInfo",
    # New Modern API (recommended)
    "observe",
    "workflow",
    "step",
    # Legacy Tracing
    "AgentTracer",
    # Legacy Monitoring - Core functions
    "monitor",
    "initialize",
    # Legacy Monitoring - Decorators
    "agent",
    "tool",
    "trace_async",
    "trace_sync",
    # Legacy Monitoring - Cost tracking
    "CostTracker",
    # Legacy Monitoring - Utilities
    "identify",
    "get_kafka_llm_monitor",
    "close_kafka_llm_monitor",
    # Utilities
    "setup_logger",
    # Converters (base interfaces only)
    "BaseConverter",
]
