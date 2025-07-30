"""
Cost calculation strategies for different LLM providers.

This module implements the Strategy pattern for calculating costs
across different providers with their specific pricing models.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any
import logging

from ..core.types import CostResult, ProviderType
from ..providers.factory import ProviderFactory

logger = logging.getLogger(__name__)


class CostCalculationStrategy(ABC):
    """Abstract base class for cost calculation strategies."""

    @abstractmethod
    def calculate_cost(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int,
        metadata: Dict[str, Any] = None,
    ) -> CostResult:
        """Calculate cost for the given model and token usage."""
        pass

    @abstractmethod
    def get_provider_type(self) -> ProviderType:
        """Get the provider type this strategy handles."""
        pass


class OpenAICostStrategy(CostCalculationStrategy):
    """Cost calculation strategy for OpenAI models."""

    def get_provider_type(self) -> ProviderType:
        return ProviderType.OPENAI

    def calculate_cost(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int,
        metadata: Dict[str, Any] = None,
    ) -> CostResult:
        """Calculate cost for OpenAI models."""
        provider = ProviderFactory.get_provider_by_type(ProviderType.OPENAI)
        model_info = provider.get_model_info(model)

        # OpenAI pricing is straightforward per-token
        input_cost = (input_tokens / 1000.0) * model_info.input_cost_per_1k
        output_cost = (output_tokens / 1000.0) * model_info.output_cost_per_1k
        total_cost = input_cost + output_cost

        return CostResult(
            input_cost=input_cost,
            output_cost=output_cost,
            total_cost=total_cost,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=input_tokens + output_tokens,
            model=model_info.name,
            provider=ProviderType.OPENAI,
        )


class AnthropicCostStrategy(CostCalculationStrategy):
    """Cost calculation strategy for Anthropic models."""

    def get_provider_type(self) -> ProviderType:
        return ProviderType.ANTHROPIC

    def calculate_cost(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int,
        metadata: Dict[str, Any] = None,
    ) -> CostResult:
        """Calculate cost for Anthropic models."""
        provider = ProviderFactory.get_provider_by_type(ProviderType.ANTHROPIC)
        model_info = provider.get_model_info(model)

        # Anthropic has standard per-token pricing
        input_cost = (input_tokens / 1000.0) * model_info.input_cost_per_1k
        output_cost = (output_tokens / 1000.0) * model_info.output_cost_per_1k
        total_cost = input_cost + output_cost

        return CostResult(
            input_cost=input_cost,
            output_cost=output_cost,
            total_cost=total_cost,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=input_tokens + output_tokens,
            model=model_info.name,
            provider=ProviderType.ANTHROPIC,
        )


class GoogleCostStrategy(CostCalculationStrategy):
    """Cost calculation strategy for Google models."""

    def get_provider_type(self) -> ProviderType:
        return ProviderType.GOOGLE

    def calculate_cost(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int,
        metadata: Dict[str, Any] = None,
    ) -> CostResult:
        """Calculate cost for Google models with context window considerations."""
        # Google has different pricing tiers based on context window usage
        context_tokens = (
            metadata.get("context_tokens", input_tokens) if metadata else input_tokens
        )

        # Default Google pricing (Gemini-1.5-pro)
        base_input_cost = 0.00125
        base_output_cost = 0.005

        # Apply context window multiplier for large contexts
        if context_tokens > 128000:
            # Long context pricing is typically 2x
            base_input_cost *= 2
            base_output_cost *= 2

        input_cost = (input_tokens / 1000.0) * base_input_cost
        output_cost = (output_tokens / 1000.0) * base_output_cost
        total_cost = input_cost + output_cost

        return CostResult(
            input_cost=input_cost,
            output_cost=output_cost,
            total_cost=total_cost,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=input_tokens + output_tokens,
            model=model,
            provider=ProviderType.GOOGLE,
        )


class DefaultCostStrategy(CostCalculationStrategy):
    """Default cost calculation strategy for unknown providers."""

    def get_provider_type(self) -> ProviderType:
        return ProviderType.UNKNOWN

    def calculate_cost(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int,
        metadata: Dict[str, Any] = None,
    ) -> CostResult:
        """Calculate cost using default pricing."""
        # Use conservative GPT-3.5-turbo pricing as default
        input_cost = (input_tokens / 1000.0) * 0.0005
        output_cost = (output_tokens / 1000.0) * 0.0015
        total_cost = input_cost + output_cost

        logger.warning(f"Using default cost calculation for unknown model: {model}")

        return CostResult(
            input_cost=input_cost,
            output_cost=output_cost,
            total_cost=total_cost,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=input_tokens + output_tokens,
            model=model,
            provider=ProviderType.UNKNOWN,
        )


class CostStrategyManager:
    """Manager for cost calculation strategies."""

    def __init__(self):
        self._strategies: Dict[ProviderType, CostCalculationStrategy] = {
            ProviderType.OPENAI: OpenAICostStrategy(),
            ProviderType.ANTHROPIC: AnthropicCostStrategy(),
            ProviderType.GOOGLE: GoogleCostStrategy(),
        }
        self._default_strategy = DefaultCostStrategy()

    def get_strategy(self, provider_type: ProviderType) -> CostCalculationStrategy:
        """Get cost calculation strategy for provider."""
        return self._strategies.get(provider_type, self._default_strategy)

    def calculate_cost(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int,
        provider_type: ProviderType = None,
        metadata: Dict[str, Any] = None,
    ) -> CostResult:
        """Calculate cost using appropriate strategy."""
        if provider_type is None:
            provider_type = ProviderFactory._detect_provider_from_model(model)

        strategy = self.get_strategy(provider_type)
        return strategy.calculate_cost(model, input_tokens, output_tokens, metadata)

    def register_strategy(
        self, provider_type: ProviderType, strategy: CostCalculationStrategy
    ):
        """Register a new cost calculation strategy."""
        self._strategies[provider_type] = strategy
