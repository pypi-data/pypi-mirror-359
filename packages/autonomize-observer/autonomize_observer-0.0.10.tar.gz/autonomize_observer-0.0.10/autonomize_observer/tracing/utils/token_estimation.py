"""
Token usage estimation utilities for LLM responses.

This module provides fallback token estimation when APIs don't return
token usage information, particularly for streaming responses.
"""

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


def estimate_token_usage_fallback(
    model_name: str, prompts: List[str], response: Any
) -> Optional[Dict[str, int]]:
    """
    Fallback method to estimate token usage using tiktoken when not provided by the API.

    Used for Azure OpenAI streaming responses that don't include token usage.

    Args:
        model_name: Name of the model used
        prompts: List of prompt strings
        response: LLM response object

    Returns:
        Dictionary with token usage or None if estimation fails
    """
    try:
        import tiktoken

        # Get encoding for the model
        if "gpt-4" in model_name.lower():
            encoding = tiktoken.get_encoding("cl100k_base")  # GPT-4 encoding
        elif "gpt-3.5" in model_name.lower():
            encoding = tiktoken.get_encoding("cl100k_base")  # GPT-3.5 encoding
        else:
            # Default to cl100k_base for most OpenAI models
            encoding = tiktoken.get_encoding("cl100k_base")

        # Count prompt tokens
        prompt_tokens = 0
        for prompt in prompts:
            if isinstance(prompt, str):
                prompt_tokens += len(encoding.encode(prompt))

        # Count completion tokens from response
        completion_tokens = 0
        response_text = _extract_response_text_for_estimation(response)

        if response_text and isinstance(response_text, str):
            completion_tokens = len(encoding.encode(response_text))

        total_tokens = prompt_tokens + completion_tokens

        if total_tokens > 0:
            logger.info(
                f"✅ Estimated tokens for {model_name}: "
                f"prompt={prompt_tokens}, completion={completion_tokens}, total={total_tokens}"
            )
            return {
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": total_tokens,
            }
        else:
            logger.warning(f"❌ Token estimation resulted in 0 tokens for {model_name}")
            return None

    except ImportError:
        logger.warning("tiktoken not available - cannot estimate token usage")
        return None
    except Exception as e:
        logger.error(f"Error in token estimation: {e}")
        return None


def _extract_response_text_for_estimation(response: Any) -> str:
    """
    Extract response text from various response formats for token estimation.

    Args:
        response: LLM response object

    Returns:
        Response text as string
    """
    try:
        # Extract response text from various response formats
        if hasattr(response, "generations") and response.generations:
            first_gen = response.generations[0]
            if isinstance(first_gen, list) and len(first_gen) > 0:
                # Streaming response - nested list
                generation = first_gen[0]
                if hasattr(generation, "text"):
                    return generation.text
                elif hasattr(generation, "message") and hasattr(
                    generation.message, "content"
                ):
                    return generation.message.content
            else:
                # Non-streaming response
                if hasattr(first_gen, "text"):
                    return first_gen.text
                elif hasattr(first_gen, "message") and hasattr(
                    first_gen.message, "content"
                ):
                    return first_gen.message.content

        return ""
    except Exception:
        return ""


def extract_token_usage_from_response(response: Any) -> Optional[Dict[str, int]]:
    """
    Extract token usage from LLM response using multiple methods.

    Args:
        response: LLM response object

    Returns:
        Token usage dictionary or None if not found
    """
    try:
        # Method 1: Non-streaming responses - llm_output
        if hasattr(response, "llm_output") and response.llm_output:
            if (
                isinstance(response.llm_output, dict)
                and "token_usage" in response.llm_output
            ):
                token_usage = response.llm_output["token_usage"]
                logger.debug(f"Found token usage in llm_output: {token_usage}")
                return token_usage

        # Method 2: Streaming responses - generations (handles nested structure)
        if hasattr(response, "generations") and response.generations:
            first_gen = response.generations[0]

            # Handle nested list structure for streaming
            if isinstance(first_gen, list) and len(first_gen) > 0:
                generation = first_gen[0]  # Get actual Generation object
            else:
                generation = first_gen  # Direct Generation object

            # Method 2a: generation.generation_info.token_usage (OpenAI/Azure streaming)
            if hasattr(generation, "generation_info") and isinstance(
                generation.generation_info, dict
            ):
                if "token_usage" in generation.generation_info:
                    token_usage = generation.generation_info["token_usage"]
                    logger.debug(f"Found token usage in generation_info: {token_usage}")
                    return token_usage

            # Method 2b: generation.message.response_metadata (Alternative streaming)
            if hasattr(generation, "message"):
                message = generation.message
                if hasattr(message, "response_metadata") and isinstance(
                    message.response_metadata, dict
                ):
                    # OpenAI format
                    if "token_usage" in message.response_metadata:
                        token_usage = message.response_metadata["token_usage"]
                        logger.debug(
                            f"Found token usage in response_metadata.token_usage: {token_usage}"
                        )
                        return token_usage
                    # Anthropic format
                    elif "usage" in message.response_metadata:
                        usage = message.response_metadata["usage"]
                        if isinstance(usage, dict):
                            # Convert Anthropic format to OpenAI format
                            token_usage = {
                                "prompt_tokens": usage.get("input_tokens", 0),
                                "completion_tokens": usage.get("output_tokens", 0),
                                "total_tokens": usage.get("input_tokens", 0)
                                + usage.get("output_tokens", 0),
                            }
                            logger.debug(
                                f"Found Anthropic usage, converted: {token_usage}"
                            )
                            return token_usage

        # Method 3: Alternative - usage_metadata (some providers)
        if hasattr(response, "usage_metadata") and isinstance(
            response.usage_metadata, dict
        ):
            token_usage = response.usage_metadata
            logger.debug(f"Found token usage in usage_metadata: {token_usage}")
            return token_usage

        return None

    except Exception as e:
        logger.debug(f"Error extracting token usage: {e}")
        return None


def extract_actual_model_name_from_response(response: Any) -> Optional[str]:
    """
    Extract the actual model name from response metadata.

    Args:
        response: LLM response object

    Returns:
        Model name from response or None if not found
    """
    try:
        # Try to get model name from response metadata (most accurate)
        if hasattr(response, "generations") and response.generations:
            first_gen = response.generations[0]

            # Handle nested list structure for streaming
            if isinstance(first_gen, list) and len(first_gen) > 0:
                generation = first_gen[0]
            else:
                generation = first_gen

            # Method 1: Check generation_info for model_name
            if hasattr(generation, "generation_info") and isinstance(
                generation.generation_info, dict
            ):
                gen_info = generation.generation_info
                if "model_name" in gen_info:
                    return gen_info["model_name"]
                elif "model" in gen_info:
                    return gen_info["model"]

            # Method 2: Check message.response_metadata for model info
            if hasattr(generation, "message") and hasattr(
                generation.message, "response_metadata"
            ):
                metadata = generation.message.response_metadata
                if isinstance(metadata, dict):
                    if "model_name" in metadata:
                        return metadata["model_name"]
                    elif "model" in metadata:
                        return metadata["model"]

        # Method 3: Check llm_output for model name (non-streaming)
        if hasattr(response, "llm_output") and isinstance(response.llm_output, dict):
            llm_output = response.llm_output
            if "model_name" in llm_output:
                return llm_output["model_name"]
            elif "model" in llm_output:
                return llm_output["model"]

        # Method 4: Check response-level metadata
        if hasattr(response, "response_metadata") and isinstance(
            response.response_metadata, dict
        ):
            metadata = response.response_metadata
            if "model_name" in metadata:
                return metadata["model_name"]
            elif "model" in metadata:
                return metadata["model"]

        return None

    except Exception as e:
        logger.debug(f"Could not extract model name from response: {e}")
        return None


def extract_response_text(response: Any) -> str:
    """
    Extract response text for sending to worker.

    Args:
        response: LLM response object

    Returns:
        Response text as string
    """
    try:
        # First check if response has a direct text attribute (not a Mock)
        if hasattr(response, "text") and isinstance(response.text, str):
            return response.text

        if hasattr(response, "generations") and response.generations:
            first_gen = response.generations[0]
            if isinstance(first_gen, list) and len(first_gen) > 0:
                generation = first_gen[0]
            else:
                generation = first_gen

            if hasattr(generation, "text") and isinstance(generation.text, str):
                return generation.text
            elif hasattr(generation, "message") and hasattr(
                generation.message, "content"
            ):
                return generation.message.content

        return str(response) if response else ""
    except Exception:
        return ""
