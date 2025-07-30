"""
Core type definitions for the Autonomize Observer SDK.

This module provides type definitions, enums, and data classes used throughout
the SDK to ensure type safety and clear interfaces.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from abc import ABC, abstractmethod


class ProviderType(str, Enum):
    """Supported LLM providers."""

    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    META = "meta"
    MISTRAL = "mistral"
    AMAZON = "amazon"
    COHERE = "cohere"
    DEEPSEEK = "deepseek"
    XAI = "xai"
    ALIBABA = "alibaba"
    PERPLEXITY = "perplexity"
    NVIDIA = "nvidia"
    UNKNOWN = "unknown"


class ModelTier(str, Enum):
    """Model performance/pricing tiers."""

    FLAGSHIP = "flagship"  # Most capable, highest cost
    ADVANCED = "advanced"  # High capability, moderate cost
    STANDARD = "standard"  # Good capability, balanced cost
    EFFICIENT = "efficient"  # Lower cost, good performance
    SPECIALIZED = "specialized"  # Specific use cases


@dataclass
class ModelInfo:
    """Information about a specific LLM model."""

    name: str
    provider: ProviderType
    tier: ModelTier
    input_cost_per_1k: float
    output_cost_per_1k: float
    context_window: Optional[int] = None
    supports_streaming: bool = True
    supports_function_calling: bool = False
    max_output_tokens: Optional[int] = None


@dataclass
class CostResult:
    """Result of cost calculation."""

    input_cost: float
    output_cost: float
    total_cost: float
    input_tokens: int
    output_tokens: int
    total_tokens: int
    model: str
    provider: ProviderType


@dataclass
class MonitorConfig:
    """Configuration for monitoring setup."""

    kafka_bootstrap_servers: Optional[str] = None
    kafka_topic: Optional[str] = None
    kafka_username: Optional[str] = None
    kafka_password: Optional[str] = None
    kafka_security_protocol: str = "PLAINTEXT"
    kafka_sasl_mechanism: str = "PLAIN"
    enable_cost_tracking: bool = True
    enable_trace_collection: bool = True
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    project_name: Optional[str] = None


@dataclass
class EventData:
    """Base class for event data."""

    event_type: str
    timestamp: float
    trace_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class LLMProvider(ABC):
    """Abstract base class for LLM provider implementations."""

    @abstractmethod
    def get_provider_type(self) -> ProviderType:
        """Get the provider type."""
        pass

    @abstractmethod
    def get_model_info(self, model_name: str) -> ModelInfo:
        """Get model information."""
        pass

    @abstractmethod
    def get_trackable_methods(self) -> List[str]:
        """Get list of methods that should be tracked."""
        pass

    @abstractmethod
    def detect_model_from_args(self, *args, **kwargs) -> Optional[str]:
        """Detect model name from method arguments."""
        pass

    @abstractmethod
    def extract_usage_info(self, response: Any) -> Dict[str, int]:
        """Extract token usage information from response."""
        pass
