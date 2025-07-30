"""
Model name utilities for LLM provider detection and cleaning.

This module provides utilities for inferring providers from model names
and cleaning/normalizing model names for consistent tracking.
"""

import logging
from typing import Any, List, Union

logger = logging.getLogger(__name__)


def guess_provider_from_model(model_name: Union[str, List[str], Any]) -> str:
    """
    Guess provider from model name using comprehensive pattern matching with type safety.

    Args:
        model_name: Model name, can be string, list, or other type

    Returns:
        Provider name or "unknown" if not detected
    """
    if not model_name:
        return "unknown"

    # Ensure we have a string (handle cases where list might be passed)
    if isinstance(model_name, list):
        if len(model_name) > 0:
            # Take first string element from list
            for item in model_name:
                if isinstance(item, str) and item.strip():
                    model_name = item
                    break
            else:
                model_name = str(model_name[0]) if model_name else "unknown"
        else:
            return "unknown"
    elif not isinstance(model_name, str):
        model_name = str(model_name)

    model_lower = model_name.lower()

    # Provider pattern mapping - easily extensible
    provider_patterns = {
        "openai": [
            "gpt",
            "openai",
            "o1",
            "o3",
            "o4",
            "davinci",
            "babbage",
            "whisper",
            "tts",
        ],
        "anthropic": ["claude", "anthropic"],
        "google": ["gemini", "google", "palm", "bard"],
        "meta": ["llama", "meta"],
        "mistral": ["mistral", "mixtral", "codestral", "pixtral"],
        "amazon": ["nova", "amazon", "bedrock"],
        "deepseek": ["deepseek"],
        "cohere": ["command", "cohere"],
        "xai": ["grok", "xai"],
        "alibaba": ["qwen", "alibaba"],
        "perplexity": ["perplexity", "sonar"],
        "nvidia": ["nemotron", "nvidia"],
    }

    for provider, patterns in provider_patterns.items():
        if any(pattern in model_lower for pattern in patterns):
            return provider

    return "unknown"


def clean_model_name(model_name: Union[str, List[str], Any]) -> str:
    """
    Clean and normalize model name using generic patterns with type safety.

    Args:
        model_name: Model name to clean

    Returns:
        Cleaned and normalized model name
    """
    if not model_name:
        return "unknown"

    # Ensure we have a string (handle cases where list might be passed)
    if isinstance(model_name, list):
        if len(model_name) > 0:
            # Take first string element from list
            for item in model_name:
                if isinstance(item, str) and item.strip():
                    model_name = item
                    break
            else:
                # If no valid string found, convert first item
                model_name = str(model_name[0]) if model_name else "unknown"
        else:
            return "unknown"
    elif not isinstance(model_name, str):
        # For non-string types (like dict, int, etc), return "unknown"
        # unless it's a simple type that could represent a model name
        if isinstance(model_name, (int, float, bool, dict, set, tuple)):
            return "unknown"
        # Convert to string for processing other types
        original_was_string = False
        model_name = str(model_name)
    else:
        original_was_string = True

    # Remove common prefixes and normalize
    cleaned = model_name.lower().strip()

    # Handle deployment prefixes generically
    prefixes_to_remove = ["azure/", "azure-", "bedrock/"]
    for prefix in prefixes_to_remove:
        if cleaned.startswith(prefix):
            cleaned = cleaned[len(prefix) :]

    # Pattern-based model detection with hierarchical fallbacks
    # Check OpenAI models
    if "gpt-4.1" in cleaned:
        if "nano" in cleaned:
            return "gpt-4.1-nano"
        elif "mini" in cleaned:
            return "gpt-4.1-mini"
        return "gpt-4.1"
    elif "gpt-4o" in cleaned or "gpt4o" in cleaned:
        if "mini" in cleaned:
            return "gpt-4o-mini"
        return "gpt-4o"
    elif "gpt-4" in cleaned:
        if "turbo" in cleaned:
            return "gpt-4-turbo"
        elif "32k" in cleaned:
            return "gpt-4-32k"
        return "gpt-4"
    elif "gpt-3.5" in cleaned or "gpt-35" in cleaned:
        if "16k" in cleaned:
            return "gpt-3.5-turbo-16k-0613"
        return "gpt-3.5-turbo"

    # Check Anthropic models
    elif "claude" in cleaned:
        if "4" in cleaned:
            if "opus" in cleaned:
                return "claude-4-opus"
            elif "sonnet" in cleaned:
                return "claude-4-sonnet"
            return "claude-4-opus"  # default
        elif "3.7" in cleaned or "3-7" in cleaned:
            return "claude-3.7-sonnet"
        elif "3.5" in cleaned or "3-5" in cleaned:
            if "haiku" in cleaned:
                return "claude-3.5-haiku"
            return "claude-3.5-sonnet"
        elif "3" in cleaned:
            if "opus" in cleaned:
                return "claude-3-opus"
            elif "haiku" in cleaned:
                return "claude-3-haiku"
            return "claude-3-sonnet"
        elif "2" in cleaned:
            return "claude-2.1"
        elif "instant" in cleaned:
            return "claude-instant-1.2"
        return "claude-3.5-sonnet"  # default

    # Check Google models
    elif "gemini" in cleaned:
        if "2.5" in cleaned:
            if "flash" in cleaned:
                if "lite" in cleaned:
                    return "gemini-2.5-flash-lite"
                return "gemini-2.5-flash"
            return "gemini-2.5-pro"
        elif "2.0" in cleaned or "2-0" in cleaned:
            if "flash" in cleaned:
                if "lite" in cleaned:
                    return "gemini-2.0-flash-lite"
                return "gemini-2.0-flash"
            return "gemini-2.0-pro"
        elif "1.5" in cleaned:
            if "flash" in cleaned:
                if "8b" in cleaned:
                    return "gemini-1.5-flash-8b"
                return "gemini-1.5-flash"
            return "gemini-1.5-pro"
        return "gemini-1.0-pro"  # default

    # Check Meta Llama models
    elif "llama" in cleaned:
        # Check more specific versions first to avoid false matches
        if "3.3" in cleaned:
            return "llama-3.3-70b"
        elif "3.2" in cleaned:
            if "90b" in cleaned:
                return "llama-3.2-90b"
            elif "11b" in cleaned:
                return "llama-3.2-11b"
            elif "3b" in cleaned:
                return "llama-3.2-3b"
            elif "1b" in cleaned:
                return "llama-3.2-1b"
        elif "3.1" in cleaned:
            if "405b" in cleaned:
                return "llama-3.1-405b"
            elif "70b" in cleaned:
                return "llama-3.1-70b"
            elif "8b" in cleaned:
                return "llama-3.1-8b"
            return "llama-3.1-8b"  # default for 3.1
        elif "llama-4-" in cleaned or (
            "4" in cleaned and "40" not in cleaned
        ):  # Avoid matching 405b as llama-4
            if "scout" in cleaned:
                return "llama-4-scout"
            elif "maverick" in cleaned:
                return "llama-4-maverick"
            elif "behemoth" in cleaned:
                return "llama-4-behemoth"
        elif "llama-3-" in cleaned or (
            "3" in cleaned and "3." not in cleaned and "13b" not in cleaned
        ):  # Avoid matching 3.x versions and 13b
            if "70b" in cleaned:
                return "llama-3-70b"
            elif "8b" in cleaned:
                return "llama-3-8b"
        elif "llama-2" in cleaned or "2" in cleaned:
            if "70b" in cleaned:
                return "llama-2-70b"
            elif "13b" in cleaned:
                return "llama-2-13b"
            elif "7b" in cleaned:
                return "llama-2-7b"
        return "llama-3-8b"  # default

    # Check Mistral models - Check specific models first, then generic patterns
    elif "codestral" in cleaned:
        return "codestral"
    elif "pixtral" in cleaned:
        return "pixtral"
    elif "mistral" in cleaned or "mixtral" in cleaned:
        if "large" in cleaned:
            if "2" in cleaned:
                return "mistral-large-2"
            return "mistral-large"
        elif "medium" in cleaned:
            return "mistral-medium"
        elif "small" in cleaned:
            return "mistral-small"
        elif "8x22b" in cleaned:
            return "mixtral-8x22b"
        elif "8x7b" in cleaned:
            return "mixtral-8x7b"
        elif "nemo" in cleaned:
            return "mistral-nemo"
        elif "7b" in cleaned:
            return "mistral-7b"
        return "mistral-small"  # default

    # Provider-based fallbacks if specific model not found
    provider = guess_provider_from_model(model_name)
    provider_defaults = {
        "openai": "gpt-3.5-turbo",
        "anthropic": "claude-3.5-sonnet",
        "google": "gemini-1.0-pro",
        "meta": "llama-3-8b",
        "mistral": "mistral-small",
    }

    if provider in provider_defaults:
        logger.debug(f"🔄 Using {provider} default model for: {model_name}")
        return provider_defaults[provider]

    # Final fallback
    # If originally non-string and no pattern matched, return "unknown"
    if "original_was_string" in locals() and not original_was_string:
        # Check if it looks like a valid model name (contains letters)
        if not any(c.isalpha() for c in model_name):
            return "unknown"

    return model_name


def infer_component_type(component_name: str, model_name: str = None) -> str:
    """
    Infer component type using generic pattern matching.

    Args:
        component_name: Name of the component
        model_name: Optional model name (if present, indicates LLM component)

    Returns:
        Component type string
    """
    if model_name:
        return "llm"  # Has model = LLM component

    # Generic pattern-based detection
    name_lower = component_name.lower()

    type_patterns = {
        "agent": ["agent", "executor", "workflow", "orchestrator"],
        "input": ["input", "prompt", "question", "query"],
        "output": ["output", "response", "result", "answer"],
        "retrieval": ["retrieval", "vector", "search", "rag", "knowledge"],
        "memory": ["memory", "history", "context", "conversation"],
        "tool": ["tool", "function", "api", "external", "utility"],
        "processing": ["process", "transform", "parse", "format"],
    }

    for component_type, patterns in type_patterns.items():
        if any(pattern in name_lower for pattern in patterns):
            return component_type

    return "component"  # Generic fallback
