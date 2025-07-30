"""
Legacy bridge for backward compatibility.

This module provides a bridge between the old monitor() function API
and the new design pattern-based implementation, ensuring 100% backward compatibility.
"""

import warnings
from typing import Any, Optional

from .enhanced_monitor import enhanced_monitor
from ..core.types import MonitorConfig


def legacy_monitor(
    client,
    provider: Optional[str] = None,
    project_name: Optional[str] = None,
    cost_rates: Optional[dict] = None,
):
    """
    Legacy monitor function with original API.

    This function maintains the exact same signature and behavior as the
    original monitor() function while using the new design patterns internally.

    Args:
        client: The LLM client to monitor
        provider: The provider name (openai, azure_openai, anthropic)
        project_name: Project name for tracking
        cost_rates: Dictionary of cost rates for different models

    Returns:
        Monitored client with observability features
    """
    # Ensure global initialization is called (for backward compatibility)
    from . import initialize

    initialize(cost_rates=cost_rates)

    # Map old provider names to new format
    provider_mapping = {
        "azure_openai": "openai",  # Azure OpenAI is still OpenAI
        "openai": "openai",
        "anthropic": "anthropic",
    }

    mapped_provider = provider_mapping.get(provider, provider) if provider else None

    # Use enhanced monitor with legacy parameters
    return enhanced_monitor(
        client=client,
        provider=mapped_provider,
        project_name=project_name,
        enable_cost_tracking=True,  # Always enabled in legacy mode
        enable_trace_collection=True,  # Always enabled in legacy mode
    )


def seamless_monitor_replacement():
    """
    Replace the existing monitor function with the legacy bridge.

    This function performs the actual replacement to ensure seamless
    backward compatibility without breaking any existing code.
    """
    import autonomize_observer.monitoring.monitor as monitor_module

    # Store original monitor function for fallback
    original_monitor = getattr(monitor_module, "monitor", None)

    def patched_monitor(
        client,
        provider: Optional[str] = None,
        project_name: Optional[str] = None,
        cost_rates: Optional[dict] = None,
    ):
        """Patched monitor function using new design patterns."""
        try:
            # Try new implementation first
            return legacy_monitor(client, provider, project_name, cost_rates)
        except Exception as e:
            # Fallback to original implementation if new one fails
            warnings.warn(
                f"New monitor implementation failed, falling back to original: {e}",
                UserWarning,
            )
            if original_monitor:
                return original_monitor(client, provider, project_name, cost_rates)
            else:
                raise RuntimeError(
                    "Both new and original monitor implementations failed"
                )

    # Replace the monitor function
    setattr(monitor_module, "monitor", patched_monitor)

    return patched_monitor
