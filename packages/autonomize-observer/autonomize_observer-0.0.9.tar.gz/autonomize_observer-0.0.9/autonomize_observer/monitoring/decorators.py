"""
Decorator pattern implementation for LLM client monitoring.

This module provides the Decorator pattern for enhancing LLM clients
with observability features while maintaining their original interface.
"""

import functools
import time
import uuid
import asyncio
import inspect
from typing import Any, Callable, Dict, List, Optional
import logging

from ..core.types import MonitorConfig, EventData, ProviderType
from ..providers.factory import ProviderFactory
from ..cost.strategies import CostStrategyManager
from ..events.system import EventSystem

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
        trackable_methods = self._provider.get_trackable_methods()

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

    def _publish_start_event(
        self,
        call_id: str,
        method_path: str,
        model_name: Optional[str],
        args: tuple,
        kwargs: dict,
    ):
        """Publish LLM call start event."""
        event_data = EventData(
            event_type="llm_call_start",
            timestamp=time.time(),
            metadata={
                "call_id": call_id,
                "method_path": method_path,
                "model": model_name,
                "provider": self._provider.get_provider_type().value,
                "user_id": self._config.user_id,
                "session_id": self._config.session_id,
                "project_name": self._config.project_name,
                # Don't log full args/kwargs for privacy
                "has_args": len(args) > 0,
                "has_kwargs": len(kwargs) > 0,
            },
        )

        self._event_system.publish("llm_call_start", event_data.__dict__)

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
        event_data = EventData(
            event_type="llm_call_end",
            timestamp=time.time(),
            metadata={
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
        )

        self._event_system.publish("llm_call_end", event_data.__dict__)

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
