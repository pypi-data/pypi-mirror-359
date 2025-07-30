"""
Modern Observer API for Autonomize Observer SDK.

This module provides the new unified API that combines monitoring and tracing
in a pythonic, intuitive interface.
"""

import asyncio
import functools
import inspect
import logging
import threading
import uuid
from contextlib import contextmanager, asynccontextmanager
from typing import Any, Dict, Optional, Union, Callable, TypeVar, cast
import weakref

from ..monitoring.monitor import (
    monitor as legacy_monitor,
    initialize as legacy_initialize,
    identify as legacy_identify,
)
from ..tracing.agent_tracer import AgentTracer, streaming_trace
from ..core.types import ProviderType
from ..providers.factory import ProviderFactory

logger = logging.getLogger(__name__)

F = TypeVar("F", bound=Callable[..., Any])

# Global registry for auto-monitoring within observe contexts
_active_observers: Dict[int, "Observer"] = {}
_observer_lock = threading.RLock()


class Observer:
    """
    Modern unified observability interface for LLM applications.

    Supports multiple usage patterns:
    - Decorator: @observe(project="my-app")
    - Context manager: with observe(project="my-app") as obs:
    - Direct monitoring: observe.monitor(client, project="my-app")
    """

    def __init__(
        self,
        project: str = "default",
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None,
        auto_detect: bool = True,
        **kwargs,
    ):
        self.project = project
        self.user_id = user_id
        self.session_id = session_id or f"session_{uuid.uuid4().hex[:8]}"
        self.tags = tags or {}
        self.auto_detect = auto_detect
        self.kwargs = kwargs

        # Observability state
        self._monitored_clients = weakref.WeakSet()
        self._active_workflow: Optional["WorkflowContext"] = None
        self._tracers = []

        # Initialize monitoring if not already done
        self._ensure_initialized()

    def _ensure_initialized(self):
        """Ensure the underlying monitoring system is initialized."""
        try:
            legacy_initialize()
        except Exception as e:
            logger.debug(f"Monitoring already initialized or failed: {e}")

    def monitor(self, client: Any, provider: Optional[str] = None) -> Any:
        """
        Monitor an LLM client for observability.

        Args:
            client: LLM client (OpenAI, Anthropic, etc.)
            provider: Provider type (auto-detected if not specified)

        Returns:
            Monitored client with observability enabled
        """
        # Auto-detect provider if not specified
        if provider is None and self.auto_detect:
            provider = self._detect_provider(client)

        # Set user context if provided
        if self.user_id or self.session_id:
            user_props = {}
            if self.user_id:
                user_props["user_id"] = self.user_id
            if self.session_id:
                user_props["session_id"] = self.session_id
            # Add any tags as user properties
            user_props.update(self.tags)
            legacy_identify(user_props)

        # Use legacy monitor with current context (only supported params)
        monitored_client = legacy_monitor(
            client,
            provider=provider,
            project_name=self.project,
            **{k: v for k, v in self.kwargs.items() if k in ["cost_rates"]},
        )

        # Track monitored client
        self._monitored_clients.add(monitored_client)

        return monitored_client

    def _detect_provider(self, client: Any) -> Optional[str]:
        """Auto-detect the provider type from client."""
        try:
            provider_type = ProviderFactory.detect_provider_from_client(client)
            return provider_type.value if provider_type else None
        except Exception as e:
            logger.debug(f"Provider detection failed: {e}")
            return None

    def workflow(self, name: str, **kwargs) -> "WorkflowContext":
        """Create a workflow context for multi-step operations."""
        return WorkflowContext(self, name, **kwargs)

    def __enter__(self):
        """Context manager entry - register for auto-monitoring."""
        thread_id = threading.get_ident()
        with _observer_lock:
            _active_observers[thread_id] = self
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - cleanup."""
        thread_id = threading.get_ident()
        with _observer_lock:
            _active_observers.pop(thread_id, None)

    async def __aenter__(self):
        """Async context manager entry."""
        return self.__enter__()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        self.__exit__(exc_type, exc_val, exc_tb)

    def __call__(self, func: F) -> F:
        """Decorator implementation."""
        if inspect.iscoroutinefunction(func):
            return cast(F, self._wrap_async_function(func))
        else:
            return cast(F, self._wrap_sync_function(func))

    def _wrap_sync_function(self, func: Callable) -> Callable:
        """Wrap synchronous function with observability."""

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            with self:
                # Auto-patch clients within this context
                with _auto_monitor_patch():
                    return func(*args, **kwargs)

        return wrapper

    def _wrap_async_function(self, func: Callable) -> Callable:
        """Wrap asynchronous function with observability."""

        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            async with self:
                # Auto-patch clients within this context
                with _auto_monitor_patch():
                    return await func(*args, **kwargs)

        return wrapper


class WorkflowContext:
    """Context manager for workflow-level observability."""

    def __init__(self, observer: Observer, name: str, **kwargs):
        self.observer = observer
        self.name = name
        self.kwargs = kwargs
        self.tracer: Optional[AgentTracer] = None

    def step(self, name: str, **kwargs) -> "StepContext":
        """Create a step within this workflow."""
        return StepContext(self, name, **kwargs)

    def __enter__(self):
        """Start workflow tracing."""
        trace_id = uuid.uuid4()
        flow_id = f"workflow_{uuid.uuid4().hex[:8]}"

        self.tracer = AgentTracer(
            trace_name=self.name,
            trace_id=trace_id,
            flow_id=flow_id,
            project_name=self.observer.project,
            user_id=self.observer.user_id,
            session_id=self.observer.session_id,
            **self.kwargs,
        )

        self.tracer.start_trace()
        self.observer._active_workflow = self
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """End workflow tracing."""
        if self.tracer:
            if exc_type:
                self.tracer.end({}, {}, error=exc_val)
            else:
                self.tracer.end({}, {})
        self.observer._active_workflow = None


class StepContext:
    """Context manager for individual workflow steps."""

    def __init__(self, workflow: WorkflowContext, name: str, **kwargs):
        self.workflow = workflow
        self.name = name
        self.kwargs = kwargs
        self.step_id = f"step_{uuid.uuid4().hex[:8]}"

    def record(
        self, inputs: Optional[Dict] = None, outputs: Optional[Dict] = None, **kwargs
    ):
        """Record step data."""
        if self.workflow.tracer:
            self.workflow.tracer.add_trace(
                self.step_id, self.name, inputs or {}, outputs or {}, **kwargs
            )

    def __enter__(self):
        """Start step tracing."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """End step tracing."""
        if exc_type and self.workflow.tracer:
            self.workflow.tracer.end_trace(self.step_id, self.name, {}, error=exc_val)


@contextmanager
def _auto_monitor_patch():
    """
    Context manager that patches common LLM client creation to auto-monitor.

    This enables the "magic" behavior within @observe decorated functions.
    """
    # Store original constructors
    originals = {}

    try:
        # Patch OpenAI client creation
        try:
            import openai

            originals["openai.OpenAI"] = openai.OpenAI
            originals["openai.AsyncOpenAI"] = openai.AsyncOpenAI

            def patched_openai_init(original_cls):
                def new_init(*args, **kwargs):
                    client = original_cls(*args, **kwargs)
                    return _auto_monitor_client(client)

                return new_init

            openai.OpenAI = patched_openai_init(openai.OpenAI)
            openai.AsyncOpenAI = patched_openai_init(openai.AsyncOpenAI)

        except ImportError:
            pass

        # Patch Anthropic client creation
        try:
            import anthropic

            originals["anthropic.Anthropic"] = anthropic.Anthropic
            originals["anthropic.AsyncAnthropic"] = anthropic.AsyncAnthropic

            def patched_anthropic_init(original_cls):
                def new_init(*args, **kwargs):
                    client = original_cls(*args, **kwargs)
                    return _auto_monitor_client(client)

                return new_init

            anthropic.Anthropic = patched_anthropic_init(anthropic.Anthropic)
            anthropic.AsyncAnthropic = patched_anthropic_init(anthropic.AsyncAnthropic)

        except ImportError:
            pass

        yield

    finally:
        # Restore original constructors
        for path, original in originals.items():
            module_name, class_name = path.rsplit(".", 1)
            try:
                module = __import__(module_name, fromlist=[class_name])
                setattr(module, class_name, original)
            except ImportError:
                pass


def _auto_monitor_client(client: Any) -> Any:
    """Auto-monitor a client if we're in an active observer context."""
    thread_id = threading.get_ident()
    with _observer_lock:
        observer = _active_observers.get(thread_id)

    if observer:
        return observer.monitor(client)
    return client


# Convenience functions for common patterns
def observe(
    project: Optional[str] = None,
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
    **kwargs,
) -> Observer:
    """
    Create an Observer instance.

    Can be used as:
    - Decorator: @observe(project="my-app")
    - Context manager: with observe(project="my-app") as obs:
    - Factory: obs = observe(project="my-app")
    """
    if project is None:
        project = "default"

    return Observer(project=project, user_id=user_id, session_id=session_id, **kwargs)


# Workflow and step decorators
def workflow(name: str, project: Optional[str] = None, **kwargs):
    """Decorator for workflow-level observability."""

    def decorator(func: F) -> F:
        obs = observe(project=project or "default", **kwargs)

        if inspect.iscoroutinefunction(func):

            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                async with obs:
                    async with obs.workflow(name) as wf:
                        with _auto_monitor_patch():
                            return await func(*args, **kwargs)

            return cast(F, async_wrapper)
        else:

            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs):
                with obs:
                    with obs.workflow(name) as wf:
                        with _auto_monitor_patch():
                            return func(*args, **kwargs)

            return cast(F, sync_wrapper)

    return decorator


def step(name: str):
    """Decorator for step-level observability within workflows."""

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Find active workflow in current thread
            thread_id = threading.get_ident()
            with _observer_lock:
                observer = _active_observers.get(thread_id)

            if observer and observer._active_workflow:
                with observer._active_workflow.step(name) as step_ctx:
                    result = func(*args, **kwargs)
                    step_ctx.record(outputs={"result": result})
                    return result
            else:
                # No active workflow, just run the function
                return func(*args, **kwargs)

        return cast(F, wrapper)

    return decorator


# Backward compatibility
class ObserverCompat:
    """Backward compatibility interface."""

    @staticmethod
    def monitor(
        client: Any, provider: Optional[str] = None, project: str = "default", **kwargs
    ) -> Any:
        """Direct monitoring for migration from old API."""
        obs = observe(project=project, **kwargs)
        return obs.monitor(client, provider=provider)


# Export the compatibility interface
observe.monitor = ObserverCompat.monitor
observe.workflow = workflow
observe.step = step
