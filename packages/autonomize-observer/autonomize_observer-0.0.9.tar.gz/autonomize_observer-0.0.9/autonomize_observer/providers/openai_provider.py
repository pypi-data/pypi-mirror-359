"""
OpenAI provider implementation.

This module provides OpenAI-specific logic for model detection,
cost calculation, and client integration.
"""

from typing import Any, Dict, List
import re

from .base import BaseLLMProvider
from ..core.types import ModelInfo, ProviderType, ModelTier


class OpenAIProvider(BaseLLMProvider):
    """OpenAI provider implementation."""

    def get_provider_type(self) -> ProviderType:
        return ProviderType.OPENAI

    def get_default_model_info(self) -> ModelInfo:
        """Default to GPT-3.5-turbo for unknown OpenAI models."""
        return ModelInfo(
            name="gpt-3.5-turbo",
            provider=ProviderType.OPENAI,
            tier=ModelTier.STANDARD,
            input_cost_per_1k=0.0005,
            output_cost_per_1k=0.0015,
            context_window=16385,
            supports_streaming=True,
            supports_function_calling=True,
        )

    def get_model_patterns(self) -> Dict[str, ModelInfo]:
        """OpenAI model patterns and information."""
        return {
            # GPT-4o series
            "gpt-4o": ModelInfo(
                name="gpt-4o",
                provider=ProviderType.OPENAI,
                tier=ModelTier.FLAGSHIP,
                input_cost_per_1k=0.001,
                output_cost_per_1k=0.004,
                context_window=128000,
                supports_streaming=True,
                supports_function_calling=True,
            ),
            "gpt-4o-mini": ModelInfo(
                name="gpt-4o-mini",
                provider=ProviderType.OPENAI,
                tier=ModelTier.EFFICIENT,
                input_cost_per_1k=0.00015,
                output_cost_per_1k=0.0006,
                context_window=128000,
                supports_streaming=True,
                supports_function_calling=True,
            ),
            # GPT-4.1 series
            "gpt-4\\.1": ModelInfo(
                name="gpt-4.1",
                provider=ProviderType.OPENAI,
                tier=ModelTier.FLAGSHIP,
                input_cost_per_1k=0.002,
                output_cost_per_1k=0.008,
                context_window=200000,
                supports_streaming=True,
                supports_function_calling=True,
            ),
            "gpt-4\\.1-mini": ModelInfo(
                name="gpt-4.1-mini",
                provider=ProviderType.OPENAI,
                tier=ModelTier.EFFICIENT,
                input_cost_per_1k=0.0004,
                output_cost_per_1k=0.0016,
                context_window=200000,
                supports_streaming=True,
                supports_function_calling=True,
            ),
            # GPT-4 series
            "gpt-4-turbo": ModelInfo(
                name="gpt-4-turbo",
                provider=ProviderType.OPENAI,
                tier=ModelTier.ADVANCED,
                input_cost_per_1k=0.01,
                output_cost_per_1k=0.03,
                context_window=128000,
                supports_streaming=True,
                supports_function_calling=True,
            ),
            "gpt-4": ModelInfo(
                name="gpt-4",
                provider=ProviderType.OPENAI,
                tier=ModelTier.ADVANCED,
                input_cost_per_1k=0.03,
                output_cost_per_1k=0.06,
                context_window=8192,
                supports_streaming=True,
                supports_function_calling=True,
            ),
            # o-series reasoning models
            "o1": ModelInfo(
                name="o1",
                provider=ProviderType.OPENAI,
                tier=ModelTier.SPECIALIZED,
                input_cost_per_1k=0.015,
                output_cost_per_1k=0.06,
                context_window=200000,
                supports_streaming=False,
                supports_function_calling=False,
            ),
            "o1-preview": ModelInfo(
                name="o1-preview",
                provider=ProviderType.OPENAI,
                tier=ModelTier.SPECIALIZED,
                input_cost_per_1k=0.015,
                output_cost_per_1k=0.06,
                context_window=128000,
                supports_streaming=False,
                supports_function_calling=False,
            ),
            "o1-mini": ModelInfo(
                name="o1-mini",
                provider=ProviderType.OPENAI,
                tier=ModelTier.EFFICIENT,
                input_cost_per_1k=0.003,
                output_cost_per_1k=0.012,
                context_window=128000,
                supports_streaming=False,
                supports_function_calling=False,
            ),
            "o3": ModelInfo(
                name="o3",
                provider=ProviderType.OPENAI,
                tier=ModelTier.SPECIALIZED,
                input_cost_per_1k=0.001,
                output_cost_per_1k=0.004,
                context_window=200000,
                supports_streaming=False,
                supports_function_calling=False,
            ),
            "o3-mini": ModelInfo(
                name="o3-mini",
                provider=ProviderType.OPENAI,
                tier=ModelTier.EFFICIENT,
                input_cost_per_1k=0.0005,
                output_cost_per_1k=0.0015,
                context_window=200000,
                supports_streaming=False,
                supports_function_calling=False,
            ),
            # GPT-3.5 series
            "gpt-3\\.5-turbo": ModelInfo(
                name="gpt-3.5-turbo",
                provider=ProviderType.OPENAI,
                tier=ModelTier.STANDARD,
                input_cost_per_1k=0.0005,
                output_cost_per_1k=0.0015,
                context_window=16385,
                supports_streaming=True,
                supports_function_calling=True,
            ),
        }

    def get_trackable_methods(self) -> List[str]:
        """Methods to track for OpenAI clients."""
        return [
            "create",
            "acreate",
            "chat.completions.create",
            "completions.create",
            "embeddings.create",
        ]

    def detect_model_from_args(self, *args, **kwargs) -> str:
        """Detect OpenAI model from method arguments."""
        # OpenAI uses 'model' parameter
        if "model" in kwargs:
            return kwargs["model"]

        # For positional arguments, model is usually not first
        # OpenAI typically requires keyword arguments
        return None

    def extract_usage_info(self, response: Any) -> Dict[str, int]:
        """Extract usage info from OpenAI response."""
        if hasattr(response, "usage"):
            usage = response.usage
            return {
                "prompt_tokens": getattr(usage, "prompt_tokens", 0),
                "completion_tokens": getattr(usage, "completion_tokens", 0),
                "total_tokens": getattr(usage, "total_tokens", 0),
            }
        elif hasattr(response, "data") and isinstance(response.data, list):
            # Embeddings response
            return {
                "prompt_tokens": getattr(response, "usage", {}).get("prompt_tokens", 0),
                "completion_tokens": 0,
                "total_tokens": getattr(response, "usage", {}).get("total_tokens", 0),
            }

        return {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
