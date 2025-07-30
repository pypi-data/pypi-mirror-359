"""
Base provider implementation for LLM providers.

This module provides the abstract base class and common functionality
for all LLM provider implementations.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Type
import re

from ..core.types import LLMProvider, ModelInfo, ProviderType, ModelTier


class BaseLLMProvider(LLMProvider):
    """Base implementation for LLM providers."""

    def __init__(self):
        self._model_cache: Dict[str, ModelInfo] = {}

    @abstractmethod
    def get_provider_type(self) -> ProviderType:
        """Get the provider type."""
        pass

    @abstractmethod
    def get_default_model_info(self) -> ModelInfo:
        """Get default model info for unknown models."""
        pass

    @abstractmethod
    def get_model_patterns(self) -> Dict[str, ModelInfo]:
        """Get regex patterns for model detection."""
        pass

    def get_model_info(self, model_name: str) -> ModelInfo:
        """Get model information with caching."""
        if model_name in self._model_cache:
            return self._model_cache[model_name]

        # Clean model name
        cleaned_name = self._clean_model_name(model_name)

        # Try exact match first
        model_patterns = self.get_model_patterns()
        if cleaned_name in model_patterns:
            model_info = model_patterns[cleaned_name]
        else:
            # Try pattern matching
            model_info = self._match_model_pattern(cleaned_name, model_patterns)
            if model_info is None:
                model_info = self.get_default_model_info()

        # Cache the result
        self._model_cache[model_name] = model_info
        return model_info

    def _clean_model_name(self, model_name: str) -> str:
        """Clean and normalize model name."""
        if not model_name:
            return "unknown"

        # Convert to lowercase and strip
        cleaned = model_name.lower().strip()

        # Remove common prefixes
        prefixes = ["azure/", "azure-", "bedrock/", "vertex/"]
        for prefix in prefixes:
            if cleaned.startswith(prefix):
                cleaned = cleaned[len(prefix) :]
                break

        return cleaned

    def _match_model_pattern(
        self, model_name: str, patterns: Dict[str, ModelInfo]
    ) -> Optional[ModelInfo]:
        """Match model name against patterns."""
        for pattern, model_info in patterns.items():
            if re.search(pattern, model_name):
                return model_info
        return None

    @abstractmethod
    def get_trackable_methods(self) -> List[str]:
        """Get list of methods that should be tracked."""
        pass

    def detect_model_from_args(self, *args, **kwargs) -> Optional[str]:
        """Default model detection from arguments."""
        # Check kwargs first
        if "model" in kwargs:
            return kwargs["model"]

        # Check args (usually first argument)
        if args and isinstance(args[0], str):
            return args[0]

        return None

    def extract_usage_info(self, response: Any) -> Dict[str, int]:
        """Default usage extraction."""
        if hasattr(response, "usage"):
            usage = response.usage
            return {
                "prompt_tokens": getattr(usage, "prompt_tokens", 0),
                "completion_tokens": getattr(usage, "completion_tokens", 0),
                "total_tokens": getattr(usage, "total_tokens", 0),
            }
        return {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
