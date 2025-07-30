"""
Provider factory for creating and managing LLM provider instances.

This module implements the Factory pattern to centralize provider creation,
model detection, and information retrieval across different LLM providers.
"""

from typing import Any, Dict, Optional, Type, Union
import re

from ..core.types import LLMProvider, ModelInfo, ProviderType
from .openai_provider import OpenAIProvider
from .anthropic_provider import AnthropicProvider


class ProviderFactory:
    """Factory for creating and managing LLM provider instances."""

    _providers: Dict[ProviderType, Type[LLMProvider]] = {
        ProviderType.OPENAI: OpenAIProvider,
        ProviderType.ANTHROPIC: AnthropicProvider,
    }

    _instances: Dict[ProviderType, LLMProvider] = {}

    @classmethod
    def create_provider(cls, client_or_model: Union[Any, str]) -> LLMProvider:
        """
        Create appropriate provider instance based on client or model name.

        Args:
            client_or_model: Either a client object or model name string

        Returns:
            LLMProvider instance for the detected provider
        """
        provider_type = cls._detect_provider(client_or_model)
        return cls._get_provider_instance(provider_type)

    @classmethod
    def get_provider_by_type(cls, provider_type: ProviderType) -> LLMProvider:
        """Get provider instance by type."""
        return cls._get_provider_instance(provider_type)

    @classmethod
    def get_model_info(cls, model_name: str) -> ModelInfo:
        """
        Get model information for any model across all providers.

        Args:
            model_name: Name of the model

        Returns:
            ModelInfo for the specified model
        """
        # First try to detect provider from model name
        provider_type = cls._detect_provider_from_model(model_name)
        provider = cls._get_provider_instance(provider_type)
        return provider.get_model_info(model_name)

    @classmethod
    def _detect_provider(cls, client_or_model: Union[Any, str]) -> ProviderType:
        """Detect provider type from client object or model name."""
        if isinstance(client_or_model, str):
            return cls._detect_provider_from_model(client_or_model)
        else:
            return cls._detect_provider_from_client(client_or_model)

    @classmethod
    def _detect_provider_from_client(cls, client: Any) -> ProviderType:
        """Detect provider from client object."""
        if client is None:
            return ProviderType.UNKNOWN

        client_class = client.__class__.__name__.lower()
        client_module = getattr(client.__class__, "__module__", "").lower()

        # OpenAI detection
        if (
            "openai" in client_class
            or "openai" in client_module
            or hasattr(client, "chat")
            and hasattr(client.chat, "completions")
        ):
            return ProviderType.OPENAI

        # Anthropic detection
        if (
            "anthropic" in client_class
            or "anthropic" in client_module
            or hasattr(client, "messages")
        ):
            return ProviderType.ANTHROPIC

        # Google detection
        if (
            "google" in client_class
            or "vertexai" in client_module
            or "genai" in client_module
        ):
            return ProviderType.GOOGLE

        return ProviderType.UNKNOWN

    @classmethod
    def _detect_provider_from_model(cls, model_name: str) -> ProviderType:
        """Detect provider from model name."""
        if not model_name:
            return ProviderType.UNKNOWN

        model_lower = model_name.lower()

        # OpenAI models
        openai_patterns = [
            r"gpt-\d",
            r"o\d+",
            r"davinci",
            r"babbage",
            r"whisper",
            r"tts-\d",
            r"text-davinci",
            r"ft:gpt",
        ]
        for pattern in openai_patterns:
            if re.search(pattern, model_lower):
                return ProviderType.OPENAI

        # Anthropic models
        if "claude" in model_lower:
            return ProviderType.ANTHROPIC

        # Google models
        if "gemini" in model_lower or "palm" in model_lower or "bard" in model_lower:
            return ProviderType.GOOGLE

        # Meta models
        if "llama" in model_lower:
            return ProviderType.META

        # Mistral models
        mistral_patterns = ["mistral", "mixtral", "codestral", "pixtral"]
        if any(pattern in model_lower for pattern in mistral_patterns):
            return ProviderType.MISTRAL

        # Amazon models
        if "nova" in model_lower or "amazon" in model_lower:
            return ProviderType.AMAZON

        # DeepSeek models
        if "deepseek" in model_lower:
            return ProviderType.DEEPSEEK

        # Cohere models
        if "command" in model_lower or "cohere" in model_lower:
            return ProviderType.COHERE

        # xAI models
        if "grok" in model_lower:
            return ProviderType.XAI

        # Alibaba models
        if "qwen" in model_lower:
            return ProviderType.ALIBABA

        # Perplexity models
        if "sonar" in model_lower or "perplexity" in model_lower:
            return ProviderType.PERPLEXITY

        # Nvidia models
        if "nemotron" in model_lower or "nvidia" in model_lower:
            return ProviderType.NVIDIA

        return ProviderType.UNKNOWN

    @classmethod
    def _get_provider_instance(cls, provider_type: ProviderType) -> LLMProvider:
        """Get or create provider instance."""
        if provider_type not in cls._instances:
            if provider_type in cls._providers:
                cls._instances[provider_type] = cls._providers[provider_type]()
            else:
                # For unsupported providers, use OpenAI as fallback
                cls._instances[provider_type] = cls._providers[ProviderType.OPENAI]()

        return cls._instances[provider_type]

    @classmethod
    def register_provider(
        cls, provider_type: ProviderType, provider_class: Type[LLMProvider]
    ):
        """Register a new provider type."""
        cls._providers[provider_type] = provider_class
        # Clear cached instance if it exists
        if provider_type in cls._instances:
            del cls._instances[provider_type]

    @classmethod
    def clear_cache(cls):
        """Clear all cached provider instances."""
        cls._instances.clear()
