"""
Decorator pattern implementation for LLM client monitoring.

This module provides the Decorator pattern for enhancing LLM clients
with observability features while maintaining their original interface.
"""

import functools
import inspect
import logging
import time
import uuid
from typing import Any, Callable, Dict, Optional

from ..core.types import EventData, MonitorConfig
from ..cost.strategies import CostStrategyManager
from ..events.system import EventSystem
from ..providers.factory import ProviderFactory

logger = logging.getLogger(__name__)


class LLMMonitoringDecorator:
    """
    Decorator that wraps LLM client methods with observability.

    This class implements the Decorator pattern to add monitoring capabilities
    to any LLM client without changing its interface.
    """

    def __init__(self, client: Any, config: MonitorConfig):
        """
        Initialize the monitoring decorator.

        Args:
            client: The LLM client to wrap
            config: Monitoring configuration
        """
        self._client = client
        self._config = config
        self._provider = ProviderFactory.create_provider(client)
        self._cost_manager = CostStrategyManager()
        self._event_system = EventSystem()

        # Track original methods to avoid double-wrapping
        self._original_methods: Dict[str, Callable] = {}

        # Wrap client methods
        self._wrap_client_methods()

    def __getattr__(self, name: str) -> Any:
        """Delegate attribute access to the wrapped client."""
        return getattr(self._client, name)

    def _wrap_client_methods(self):
        """Wrap all trackable methods of the client."""
        try:
            trackable_methods = self._provider.get_trackable_methods()
        except AttributeError as e:
            logger.debug(f"Failed to get trackable methods: {e}")
            return

        for method_path in trackable_methods:
            try:
                self._wrap_method(method_path)
            except AttributeError as e:
                logger.debug(f"Method {method_path} not found on client: {e}")
                continue

    def _wrap_method(self, method_path: str):
        """
        Wrap a specific method with monitoring.

        Args:
            method_path: Dot-separated path to the method (e.g., 'chat.completions.create')
        """
        # Navigate to the method
        obj = self._client
        path_parts = method_path.split(".")

        # Navigate to the parent object
        for part in path_parts[:-1]:
            if hasattr(obj, part):
                obj = getattr(obj, part)
            else:
                return  # Method path doesn't exist

        method_name = path_parts[-1]
        if not hasattr(obj, method_name):
            return  # Method doesn't exist

        original_method = getattr(obj, method_name)

        # Store original method
        self._original_methods[method_path] = original_method

        # Check if method is async
        if inspect.iscoroutinefunction(original_method):
            wrapped_method = self._create_async_wrapper(original_method, method_path)
        else:
            wrapped_method = self._create_sync_wrapper(original_method, method_path)

        # Replace method with wrapped version
        setattr(obj, method_name, wrapped_method)

    def _create_sync_wrapper(
        self, original_method: Callable, method_path: str
    ) -> Callable:
        """Create synchronous wrapper for a method."""

        @functools.wraps(original_method)
        def wrapper(*args, **kwargs):
            return self._execute_sync_monitoring(
                original_method, method_path, *args, **kwargs
            )

        return wrapper

    def _create_async_wrapper(
        self, original_method: Callable, method_path: str
    ) -> Callable:
        """Create asynchronous wrapper for a method."""

        @functools.wraps(original_method)
        async def wrapper(*args, **kwargs):
            return await self._execute_async_monitoring(
                original_method, method_path, *args, **kwargs
            )

        return wrapper

    def _execute_sync_monitoring(
        self, original_method: Callable, method_path: str, *args, **kwargs
    ) -> Any:
        """Execute sync method with monitoring wrapper."""
        # Generate tracking IDs
        call_id = str(uuid.uuid4())
        start_time = time.time()

        # Extract model information
        model_name = self._provider.detect_model_from_args(*args, **kwargs)

        try:
            # Publish start event
            self._publish_start_event(call_id, method_path, model_name, args, kwargs)

            # Execute original method
            result = original_method(*args, **kwargs)

            # Check if this is a streaming response
            # Only consider it streaming if stream=True was explicitly passed
            is_streaming = kwargs.get("stream", False) is True

            if is_streaming:
                # Handle streaming response
                return self._handle_streaming_response(
                    result, call_id, method_path, model_name, start_time
                )

            # Calculate timing
            end_time = time.time()
            duration_ms = (end_time - start_time) * 1000

            # Extract usage information
            usage_info = self._provider.extract_usage_info(result)

            # Calculate cost if enabled
            cost_result = None
            if self._config.enable_cost_tracking and model_name:
                try:
                    cost_result = self._cost_manager.calculate_cost(
                        model=model_name,
                        input_tokens=usage_info.get("prompt_tokens", 0),
                        output_tokens=usage_info.get("completion_tokens", 0),
                        provider_type=self._provider.get_provider_type(),
                    )
                except Exception as e:
                    logger.warning(f"Cost calculation failed: {e}")

            # Publish end event
            self._publish_end_event(
                call_id,
                method_path,
                model_name,
                result,
                usage_info,
                duration_ms,
                cost_result,
            )

            return result

        except Exception as e:
            # Calculate timing for error case
            end_time = time.time()
            duration_ms = (end_time - start_time) * 1000

            # Publish error event
            self._publish_error_event(
                call_id, method_path, model_name, str(e), duration_ms
            )

            # Re-raise the exception
            raise

    async def _execute_async_monitoring(
        self, original_method: Callable, method_path: str, *args, **kwargs
    ) -> Any:
        """Execute async method with monitoring wrapper."""
        # Generate tracking IDs
        call_id = str(uuid.uuid4())
        start_time = time.time()

        # Extract model information
        model_name = self._provider.detect_model_from_args(*args, **kwargs)

        try:
            # Publish start event
            self._publish_start_event(call_id, method_path, model_name, args, kwargs)

            # Execute original method
            result = await original_method(*args, **kwargs)

            # Check if this is a streaming response
            # Only consider it streaming if stream=True was explicitly passed
            is_streaming = kwargs.get("stream", False) is True

            if is_streaming:
                # Handle async streaming response
                return await self._handle_async_streaming_response(
                    result, call_id, method_path, model_name, start_time
                )

            # Calculate timing
            end_time = time.time()
            duration_ms = (end_time - start_time) * 1000

            # Extract usage information
            usage_info = self._provider.extract_usage_info(result)

            # Calculate cost if enabled
            cost_result = None
            if self._config.enable_cost_tracking and model_name:
                try:
                    cost_result = self._cost_manager.calculate_cost(
                        model=model_name,
                        input_tokens=usage_info.get("prompt_tokens", 0),
                        output_tokens=usage_info.get("completion_tokens", 0),
                        provider_type=self._provider.get_provider_type(),
                    )
                except Exception as e:
                    logger.warning(f"Cost calculation failed: {e}")

            # Publish end event
            self._publish_end_event(
                call_id,
                method_path,
                model_name,
                result,
                usage_info,
                duration_ms,
                cost_result,
            )

            return result

        except Exception as e:
            # Calculate timing for error case
            end_time = time.time()
            duration_ms = (end_time - start_time) * 1000

            # Publish error event
            self._publish_error_event(
                call_id, method_path, model_name, str(e), duration_ms
            )

            # Re-raise the exception
            raise

    def _handle_streaming_response(
        self, 
        stream_response,
        call_id: str,
        method_path: str,
        model_name: Optional[str],
        start_time: float
    ):
        """Handle streaming response by collecting chunks."""
        class StreamingWrapper:
            def __init__(self, stream, decorator, call_id, method_path, model_name, start_time):
                self.stream = stream
                self.decorator = decorator
                self.call_id = call_id
                self.method_path = method_path
                self.model_name = model_name
                self.start_time = start_time
                self.chunks = []
                self.complete_content = ""
                self.usage_info = {}
                self.final_response = None
                
            def __iter__(self):
                return self
                
            def __next__(self):
                try:
                    chunk = next(self.stream)
                    
                    # Collect chunk content
                    if hasattr(chunk, "choices") and chunk.choices:
                        choice = chunk.choices[0]
                        if hasattr(choice, "delta") and hasattr(choice.delta, "content"):
                            if choice.delta.content is not None:
                                self.complete_content += choice.delta.content
                                
                        # Check for usage info in the last chunk
                        if hasattr(chunk, "usage") and chunk.usage:
                            self.usage_info = {
                                "prompt_tokens": chunk.usage.prompt_tokens,
                                "completion_tokens": chunk.usage.completion_tokens,
                                "total_tokens": chunk.usage.total_tokens,
                            }
                            
                    self.chunks.append(chunk)
                    return chunk
                    
                except StopIteration:
                    # Stream is complete, send end event
                    self._finalize()
                    raise
                    
            def _finalize(self):
                """Send the end event with complete response."""
                end_time = time.time()
                duration_ms = (end_time - self.start_time) * 1000
                
                # Create a mock response object with the complete content
                mock_response = type('Response', (), {
                    'choices': [type('Choice', (), {
                        'message': type('Message', (), {
                            'content': self.complete_content
                        })()
                    })()],
                    'usage': type('Usage', (), self.usage_info)() if self.usage_info else None
                })
                
                # Calculate cost if enabled
                cost_result = None
                if self.decorator._config.enable_cost_tracking and self.model_name and self.usage_info:
                    try:
                        cost_result = self.decorator._cost_manager.calculate_cost(
                            model=self.model_name,
                            input_tokens=self.usage_info.get("prompt_tokens", 0),
                            output_tokens=self.usage_info.get("completion_tokens", 0),
                            provider_type=self.decorator._provider.get_provider_type(),
                        )
                    except Exception as e:
                        logger.warning(f"Cost calculation failed: {e}")
                
                # Publish end event with complete content
                self.decorator._publish_end_event(
                    self.call_id,
                    self.method_path,
                    self.model_name,
                    mock_response,
                    self.usage_info,
                    duration_ms,
                    cost_result,
                )
                
        return StreamingWrapper(stream_response, self, call_id, method_path, model_name, start_time)
    
    async def _handle_async_streaming_response(
        self, 
        stream_response,
        call_id: str,
        method_path: str,
        model_name: Optional[str],
        start_time: float
    ):
        """Handle async streaming response by collecting chunks."""
        class AsyncStreamingWrapper:
            def __init__(self, stream, decorator, call_id, method_path, model_name, start_time):
                self.stream = stream
                self.decorator = decorator
                self.call_id = call_id
                self.method_path = method_path
                self.model_name = model_name
                self.start_time = start_time
                self.chunks = []
                self.complete_content = ""
                self.usage_info = {}
                
            def __aiter__(self):
                return self
                
            async def __anext__(self):
                try:
                    chunk = await self.stream.__anext__()
                    
                    # Collect chunk content
                    if hasattr(chunk, "choices") and chunk.choices:
                        choice = chunk.choices[0]
                        if hasattr(choice, "delta") and hasattr(choice.delta, "content"):
                            if choice.delta.content is not None:
                                self.complete_content += choice.delta.content
                                
                        # Check for usage info in the last chunk
                        if hasattr(chunk, "usage") and chunk.usage:
                            self.usage_info = {
                                "prompt_tokens": chunk.usage.prompt_tokens,
                                "completion_tokens": chunk.usage.completion_tokens,
                                "total_tokens": chunk.usage.total_tokens,
                            }
                            
                    self.chunks.append(chunk)
                    return chunk
                    
                except StopAsyncIteration:
                    # Stream is complete, send end event
                    await self._finalize()
                    raise
                    
            async def _finalize(self):
                """Send the end event with complete response."""
                end_time = time.time()
                duration_ms = (end_time - self.start_time) * 1000
                
                # Create a mock response object with the complete content
                mock_response = type('Response', (), {
                    'choices': [type('Choice', (), {
                        'message': type('Message', (), {
                            'content': self.complete_content
                        })()
                    })()],
                    'usage': type('Usage', (), self.usage_info)() if self.usage_info else None
                })
                
                # Calculate cost if enabled
                cost_result = None
                if self.decorator._config.enable_cost_tracking and self.model_name and self.usage_info:
                    try:
                        cost_result = self.decorator._cost_manager.calculate_cost(
                            model=self.model_name,
                            input_tokens=self.usage_info.get("prompt_tokens", 0),
                            output_tokens=self.usage_info.get("completion_tokens", 0),
                            provider_type=self.decorator._provider.get_provider_type(),
                        )
                    except Exception as e:
                        logger.warning(f"Cost calculation failed: {e}")
                
                # Publish end event with complete content
                self.decorator._publish_end_event(
                    self.call_id,
                    self.method_path,
                    self.model_name,
                    mock_response,
                    self.usage_info,
                    duration_ms,
                    cost_result,
                )
                
        return AsyncStreamingWrapper(stream_response, self, call_id, method_path, model_name, start_time)
    
    def _publish_start_event(
        self,
        call_id: str,
        method_path: str,
        model_name: Optional[str],
        args: tuple,
        kwargs: dict,
    ):
        """Publish LLM call start event."""
        # Extract messages and params from kwargs (typical for OpenAI/Anthropic style calls)
        messages = kwargs.get("messages", [])
        params = {k: v for k, v in kwargs.items() if k not in ["messages", "api_key"]}
        
        event_dict = {
            "event_type": "llm_call_start",
            "timestamp": time.time(),
            "metadata": {
                "call_id": call_id,
                "method_path": method_path,
                "model": model_name,
                "provider": self._provider.get_provider_type().value,
                "user_id": self._config.user_id,
                "session_id": self._config.session_id,
                "project_name": self._config.project_name,
                "has_args": len(args) > 0,
                "has_kwargs": len(kwargs) > 0,
            },
            "messages": messages,
            "params": params,
        }

        self._event_system.publish("llm_call_start", event_dict)

    def _publish_end_event(
        self,
        call_id: str,
        method_path: str,
        model_name: Optional[str],
        response: Any,
        usage_info: Dict[str, int],
        duration_ms: float,
        cost_result: Optional[Any] = None,
    ):
        """Publish LLM call end event."""
        # Extract response text from different provider formats
        response_text = ""
        try:
            # OpenAI style response (most common)
            if hasattr(response, "choices") and response.choices:
                choice = response.choices[0]
                if hasattr(choice, "message") and hasattr(choice.message, "content"):
                    response_text = choice.message.content or ""
                elif hasattr(choice, "text"):
                    response_text = choice.text or ""
            # Anthropic style response  
            elif hasattr(response, "content"):
                if isinstance(response.content, list) and response.content:
                    # Handle content blocks
                    content = response.content[0]
                    if hasattr(content, "text"):
                        response_text = content.text or ""
                elif isinstance(response.content, str):
                    response_text = response.content
            # Direct string response
            elif isinstance(response, str):
                response_text = response
            # Dictionary response
            elif isinstance(response, dict):
                response_text = response.get("content", "") or response.get("text", "") or str(response)
        except Exception:
            # If extraction fails, use a placeholder
            response_text = ""
            
        event_dict = {
            "event_type": "llm_call_end",
            "timestamp": time.time(),
            "metadata": {
                "call_id": call_id,
                "method_path": method_path,
                "model": model_name,
                "provider": self._provider.get_provider_type().value,
                "duration_ms": duration_ms,
                "usage": usage_info,
                "cost": cost_result.__dict__ if cost_result else None,
                "user_id": self._config.user_id,
                "session_id": self._config.session_id,
                "project_name": self._config.project_name,
            },
            "response": response_text,
        }

        self._event_system.publish("llm_call_end", event_dict)

    def _publish_error_event(
        self,
        call_id: str,
        method_path: str,
        model_name: Optional[str],
        error_message: str,
        duration_ms: float,
    ):
        """Publish LLM call error event."""
        event_data = EventData(
            event_type="llm_call_error",
            timestamp=time.time(),
            metadata={
                "call_id": call_id,
                "method_path": method_path,
                "model": model_name,
                "provider": self._provider.get_provider_type().value,
                "duration_ms": duration_ms,
                "error": error_message,
                "user_id": self._config.user_id,
                "session_id": self._config.session_id,
                "project_name": self._config.project_name,
            },
        )

        self._event_system.publish("llm_call_error", event_data.__dict__)

    def get_event_system(self) -> EventSystem:
        """Get the event system for custom event handling."""
        return self._event_system

    def unwrap(self) -> Any:
        """
        Remove monitoring and return original client.

        Returns:
            The original unwrapped client
        """
        # Restore original methods
        for method_path, original_method in self._original_methods.items():
            obj = self._client
            path_parts = method_path.split(".")

            # Navigate to parent object
            for part in path_parts[:-1]:
                obj = getattr(obj, part)

            # Restore original method
            setattr(obj, path_parts[-1], original_method)

        return self._client
