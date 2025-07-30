"""
LangChain callback handler for streaming cost tracking.

This module provides the StreamingLangChainCallback class that integrates
with LangChain to track LLM calls and token usage in real-time.
"""

import logging
import time
from typing import Any, Dict, List, Optional

from ...kafka.schemas import _safe_serialize_value
from ..utils.model_utils import guess_provider_from_model
from ..utils.token_estimation import (
    estimate_token_usage_fallback,
    extract_actual_model_name_from_response,
    extract_response_text,
    extract_token_usage_from_response,
)

# Import LangChain if available
try:
    from langchain.callbacks.base import BaseCallbackHandler

    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    BaseCallbackHandler = object

logger = logging.getLogger(__name__)


class StreamingLangChainCallback(BaseCallbackHandler):
    """LangChain callback for streaming cost tracking."""

    def __init__(self, tracer):
        super().__init__()
        self.tracer = tracer

        # Lightweight streaming mode - no cost calculation (done in worker)
        self.cost_tracker = None

        # Track active LLM runs for streaming mode
        self.llm_runs = {}

    def on_llm_start(
        self, serialized: Dict[str, Any], prompts: List[str], **kwargs
    ) -> None:
        """
        Track LLM start using proven agent_tracer logic.
        """
        try:
            run_id = str(kwargs.get("run_id", ""))
            if not run_id:
                return

            model_name = self._extract_model_name_from_start(serialized, kwargs)
            logger.debug(f"🔍 Extracted model name in on_llm_start: {model_name}")

            # Store run info for cost calculation
            self.llm_runs[run_id] = {
                "model_name": model_name,
                "start_time": time.time(),
                "prompts": prompts,
                "serialized": serialized,
            }

            # Send real-time LLM start event
            self._send_llm_start_event(run_id, model_name, prompts)

        except Exception as e:
            logger.error(f"❌ Critical error in on_llm_start: {e}")

    def on_llm_end(self, response, **kwargs) -> None:
        """
        End LLM run using proven agent_tracer logic.
        """
        try:
            run_id = str(kwargs.get("run_id", ""))
            if not run_id or run_id not in self.llm_runs:
                return

            run_info = self.llm_runs[run_id]

            # Extract token usage and model name using proven agent_tracer logic
            model_name = run_info["model_name"]

            # Try to get the actual model name from response metadata (more accurate)
            actual_model_name = extract_actual_model_name_from_response(response)
            if actual_model_name:
                model_name = actual_model_name
                logger.debug(f"Updated model name from response: {model_name}")

            # Extract token usage from response
            token_usage = extract_token_usage_from_response(response)

            # Send token usage if found, otherwise try fallback estimation
            if token_usage and isinstance(token_usage, dict):
                self._send_llm_end_event_with_usage(
                    run_id, model_name, run_info, response, token_usage
                )
                logger.info(
                    f"✅ Sent llm_end event for {model_name} with API token usage"
                )
            else:
                # FALLBACK: Estimate token usage for Azure OpenAI streaming responses
                logger.info(
                    f"🔄 No token usage found - attempting fallback estimation for {model_name}"
                )
                self._handle_fallback_token_estimation(
                    run_id, model_name, run_info, response
                )

        except Exception as e:
            logger.error(f"Error in on_llm_end: {e}")
        finally:
            # Clean up run info
            if run_id in self.llm_runs:
                del self.llm_runs[run_id]

    def on_llm_error(self, error: Exception, **kwargs) -> None:
        """Handle LLM errors."""
        run_id = str(kwargs.get("run_id", ""))
        if run_id in self.llm_runs:
            del self.llm_runs[run_id]

    def on_chat_model_start(
        self, serialized: Dict[str, Any], messages: List[List], **kwargs
    ) -> None:
        """Handle chat model start (same as LLM start for our purposes)."""
        # Convert messages to prompts format for compatibility
        prompts = self._convert_messages_to_prompts(messages)

        # Delegate to on_llm_start
        self.on_llm_start(serialized, prompts, **kwargs)

    def _extract_model_name_from_start(
        self, serialized: Dict[str, Any], kwargs: Dict[str, Any]
    ) -> str:
        """Extract model name from LLM start parameters using multiple methods."""
        model_name = "unknown"

        # PROVEN LOGIC from agent_tracer.py - Method 1: Extract from kwargs (most reliable)
        if "kwargs" in kwargs and isinstance(kwargs["kwargs"], dict):
            run_kwargs = kwargs["kwargs"]
            if "model" in run_kwargs:
                model_name = run_kwargs["model"]
            elif "model_name" in run_kwargs:
                model_name = run_kwargs["model_name"]

        # Method 2: Extract from serialized kwargs (backup)
        if model_name == "unknown" and "kwargs" in serialized:
            serialized_kwargs = serialized.get("kwargs", {})
            if isinstance(serialized_kwargs, dict):
                if "model" in serialized_kwargs:
                    model_name = serialized_kwargs["model"]
                elif "model_name" in serialized_kwargs:
                    model_name = serialized_kwargs["model_name"]

        # Method 3: Extract from component invocation kwargs (LangFlow specific)
        if model_name == "unknown" and "invocation_params" in kwargs:
            invocation_params = kwargs.get("invocation_params", {})
            if isinstance(invocation_params, dict):
                if "model" in invocation_params:
                    model_name = invocation_params["model"]
                elif "model_name" in invocation_params:
                    model_name = invocation_params["model_name"]

        # Method 4: FALLBACK ONLY - Extract from serialized info (class name - not reliable)
        if (
            model_name == "unknown"
            and "id" in serialized
            and isinstance(serialized["id"], list)
        ):
            class_name = serialized["id"][-1]
            # Only use class name if no other method worked
            model_name = class_name
            logger.warning(
                f"⚠️ Using LangChain class name as model name fallback: {model_name}"
            )

        return model_name

    def _convert_messages_to_prompts(self, messages: List[List]) -> List[str]:
        """Convert message objects to prompts format for compatibility."""
        prompts = []
        for message_list in messages:
            # Convert message objects to string representation
            prompt_parts = []
            for msg in message_list:
                if hasattr(msg, "content"):
                    prompt_parts.append(str(msg.content))
                else:
                    prompt_parts.append(str(msg))
            prompts.append("\n".join(prompt_parts))
        return prompts

    def _send_llm_start_event(
        self, run_id: str, model_name: str, prompts: List[str]
    ) -> None:
        """Send LLM start event to Kafka."""
        if self.tracer._trace_context and self.tracer._kafka_producer:
            try:
                provider = guess_provider_from_model(model_name)
                self.tracer._kafka_producer.send_custom_event(
                    trace_id=self.tracer._trace_context.trace_id,
                    event_type="llm_start",
                    data={
                        "run_id": run_id,
                        "model_info": {
                            "name": model_name,
                            "provider": provider,
                        },
                        "prompts": _safe_serialize_value(prompts),
                    },
                )
                logger.info(f"✅ Sent llm_start event for {model_name}")
            except Exception as e:
                logger.error(f"❌ Failed to send llm_start event: {e}")

    def _send_llm_end_event_with_usage(
        self,
        run_id: str,
        model_name: str,
        run_info: Dict[str, Any],
        response: Any,
        token_usage: Dict[str, int],
    ) -> None:
        """Send LLM end event with token usage to Kafka."""
        if self.tracer._trace_context and self.tracer._kafka_producer:
            self.tracer._kafka_producer.send_custom_event(
                trace_id=self.tracer._trace_context.trace_id,
                event_type="llm_end",
                data={
                    "run_id": run_id,
                    "model_name": model_name,
                    "prompts": run_info.get("prompts", []),
                    "response_data": extract_response_text(response),
                    "token_usage": token_usage,
                },
            )

    def _handle_fallback_token_estimation(
        self, run_id: str, model_name: str, run_info: Dict[str, Any], response: Any
    ) -> None:
        """Handle fallback token estimation when API doesn't provide usage."""
        try:
            # Try to estimate token usage using tiktoken
            estimated_tokens = estimate_token_usage_fallback(
                model_name=model_name,
                prompts=run_info.get("prompts", []),
                response=response,
            )

            if estimated_tokens:
                # Send llm_end event with estimated token usage
                if self.tracer._trace_context and self.tracer._kafka_producer:
                    self.tracer._kafka_producer.send_custom_event(
                        trace_id=self.tracer._trace_context.trace_id,
                        event_type="llm_end",
                        data={
                            "run_id": run_id,
                            "model_name": model_name,
                            "prompts": run_info.get("prompts", []),
                            "response_data": extract_response_text(response),
                            "token_usage": estimated_tokens,
                        },
                    )
                logger.info(
                    f"✅ Sent llm_end event for {model_name} with estimated tokens"
                )
            else:
                logger.warning(
                    f"❌ Could not estimate token usage for model {model_name}"
                )

        except Exception as e:
            logger.error(f"Error estimating token usage: {e}")
