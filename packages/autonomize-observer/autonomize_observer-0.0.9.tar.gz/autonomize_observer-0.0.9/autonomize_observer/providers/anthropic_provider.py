"""
Anthropic provider implementation.

This module provides Anthropic-specific logic for model detection,
cost calculation, and client integration.
"""

from typing import Any, Dict, List

from .base import BaseLLMProvider
from ..core.types import ModelInfo, ProviderType, ModelTier


class AnthropicProvider(BaseLLMProvider):
    """Anthropic provider implementation."""

    def get_provider_type(self) -> ProviderType:
        return ProviderType.ANTHROPIC

    def get_default_model_info(self) -> ModelInfo:
        """Default to Claude-3-sonnet for unknown Anthropic models."""
        return ModelInfo(
            name="claude-3-sonnet",
            provider=ProviderType.ANTHROPIC,
            tier=ModelTier.ADVANCED,
            input_cost_per_1k=0.003,
            output_cost_per_1k=0.015,
            context_window=200000,
            supports_streaming=True,
            supports_function_calling=True,
        )

    def get_model_patterns(self) -> Dict[str, ModelInfo]:
        """Anthropic model patterns and information."""
        return {
            # Claude 4 series
            "claude-4-opus": ModelInfo(
                name="claude-4-opus",
                provider=ProviderType.ANTHROPIC,
                tier=ModelTier.FLAGSHIP,
                input_cost_per_1k=0.015,
                output_cost_per_1k=0.075,
                context_window=200000,
                supports_streaming=True,
                supports_function_calling=True,
            ),
            "claude-4-sonnet": ModelInfo(
                name="claude-4-sonnet",
                provider=ProviderType.ANTHROPIC,
                tier=ModelTier.ADVANCED,
                input_cost_per_1k=0.003,
                output_cost_per_1k=0.015,
                context_window=200000,
                supports_streaming=True,
                supports_function_calling=True,
            ),
            # Claude 3.7 series
            "claude-3\\.7-sonnet": ModelInfo(
                name="claude-3.7-sonnet",
                provider=ProviderType.ANTHROPIC,
                tier=ModelTier.ADVANCED,
                input_cost_per_1k=0.003,
                output_cost_per_1k=0.015,
                context_window=200000,
                supports_streaming=True,
                supports_function_calling=True,
            ),
            # Claude 3.5 series
            "claude-3\\.5-sonnet": ModelInfo(
                name="claude-3.5-sonnet",
                provider=ProviderType.ANTHROPIC,
                tier=ModelTier.ADVANCED,
                input_cost_per_1k=0.003,
                output_cost_per_1k=0.015,
                context_window=200000,
                supports_streaming=True,
                supports_function_calling=True,
            ),
            "claude-3\\.5-haiku": ModelInfo(
                name="claude-3.5-haiku",
                provider=ProviderType.ANTHROPIC,
                tier=ModelTier.EFFICIENT,
                input_cost_per_1k=0.0008,
                output_cost_per_1k=0.004,
                context_window=200000,
                supports_streaming=True,
                supports_function_calling=True,
            ),
            # Claude 3 series
            "claude-3-opus": ModelInfo(
                name="claude-3-opus",
                provider=ProviderType.ANTHROPIC,
                tier=ModelTier.FLAGSHIP,
                input_cost_per_1k=0.015,
                output_cost_per_1k=0.075,
                context_window=200000,
                supports_streaming=True,
                supports_function_calling=True,
            ),
            "claude-3-sonnet": ModelInfo(
                name="claude-3-sonnet",
                provider=ProviderType.ANTHROPIC,
                tier=ModelTier.ADVANCED,
                input_cost_per_1k=0.003,
                output_cost_per_1k=0.015,
                context_window=200000,
                supports_streaming=True,
                supports_function_calling=True,
            ),
            "claude-3-haiku": ModelInfo(
                name="claude-3-haiku",
                provider=ProviderType.ANTHROPIC,
                tier=ModelTier.EFFICIENT,
                input_cost_per_1k=0.00025,
                output_cost_per_1k=0.00125,
                context_window=200000,
                supports_streaming=True,
                supports_function_calling=True,
            ),
            # Claude 2 series
            "claude-2\\.1": ModelInfo(
                name="claude-2.1",
                provider=ProviderType.ANTHROPIC,
                tier=ModelTier.STANDARD,
                input_cost_per_1k=0.008,
                output_cost_per_1k=0.024,
                context_window=200000,
                supports_streaming=True,
                supports_function_calling=False,
            ),
            "claude-2": ModelInfo(
                name="claude-2",
                provider=ProviderType.ANTHROPIC,
                tier=ModelTier.STANDARD,
                input_cost_per_1k=0.008,
                output_cost_per_1k=0.024,
                context_window=100000,
                supports_streaming=True,
                supports_function_calling=False,
            ),
            "claude-instant": ModelInfo(
                name="claude-instant-1.2",
                provider=ProviderType.ANTHROPIC,
                tier=ModelTier.EFFICIENT,
                input_cost_per_1k=0.0008,
                output_cost_per_1k=0.0024,
                context_window=100000,
                supports_streaming=True,
                supports_function_calling=False,
            ),
        }

    def get_trackable_methods(self) -> List[str]:
        """Methods to track for Anthropic clients."""
        return [
            "messages.create",
            "messages.stream",
            "completions.create",
        ]

    def detect_model_from_args(self, *args, **kwargs) -> str:
        """Detect Anthropic model from method arguments."""
        # Anthropic uses 'model' parameter
        if "model" in kwargs:
            return kwargs["model"]

        return None

    def extract_usage_info(self, response: Any) -> Dict[str, int]:
        """Extract usage info from Anthropic response."""
        if hasattr(response, "usage"):
            usage = response.usage
            return {
                "prompt_tokens": getattr(usage, "input_tokens", 0),
                "completion_tokens": getattr(usage, "output_tokens", 0),
                "total_tokens": getattr(usage, "input_tokens", 0)
                + getattr(usage, "output_tokens", 0),
            }

        return {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
