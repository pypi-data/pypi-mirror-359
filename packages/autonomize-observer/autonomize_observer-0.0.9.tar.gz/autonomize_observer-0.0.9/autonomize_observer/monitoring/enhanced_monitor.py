"""
Enhanced monitor function implementation using design patterns.

This module provides the refactored monitor() function that uses the new
design patterns while maintaining 100% backward compatibility.
"""

import os
from typing import Any, Optional
import warnings

from ..core.types import MonitorConfig
from ..monitoring.decorators import LLMMonitoringDecorator
from ..events.system import get_global_event_system


def enhanced_monitor(
    client: Any,
    provider: Optional[str] = None,
    kafka_bootstrap_servers: Optional[str] = None,
    kafka_topic: Optional[str] = None,
    kafka_username: Optional[str] = None,
    kafka_password: Optional[str] = None,
    kafka_security_protocol: str = "PLAINTEXT",
    kafka_sasl_mechanism: str = "PLAIN",
    enable_cost_tracking: bool = True,
    enable_trace_collection: bool = True,
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
    project_name: Optional[str] = None,
    **kwargs,
) -> Any:
    """
    Enhanced monitor function using design patterns.

    This function wraps LLM clients with observability features using the
    Decorator pattern and other design patterns for better maintainability.

    Args:
        client: The LLM client to monitor
        provider: Provider type (auto-detected if not specified)
        kafka_bootstrap_servers: Kafka broker addresses
        kafka_topic: Kafka topic for events
        kafka_username: Kafka SASL username
        kafka_password: Kafka SASL password
        kafka_security_protocol: Kafka security protocol
        kafka_sasl_mechanism: Kafka SASL mechanism
        enable_cost_tracking: Whether to track costs
        enable_trace_collection: Whether to collect traces
        user_id: User identifier
        session_id: Session identifier
        project_name: Project name
        **kwargs: Additional configuration options

    Returns:
        Monitored client with observability features
    """
    if client is None:
        warnings.warn("Cannot monitor None client", UserWarning)
        return None

    # Create configuration with environment variable defaults
    config = MonitorConfig(
        kafka_bootstrap_servers=kafka_bootstrap_servers
        or os.getenv("AUTONOMIZE_KAFKA_BROKERS", "localhost:9092"),
        kafka_topic=kafka_topic
        or os.getenv("AUTONOMIZE_KAFKA_TOPIC", "genesis-traces"),
        kafka_username=kafka_username or os.getenv("AUTONOMIZE_KAFKA_USERNAME"),
        kafka_password=kafka_password or os.getenv("AUTONOMIZE_KAFKA_PASSWORD"),
        kafka_security_protocol=kafka_security_protocol,
        kafka_sasl_mechanism=kafka_sasl_mechanism,
        enable_cost_tracking=enable_cost_tracking,
        enable_trace_collection=enable_trace_collection,
        user_id=user_id,
        session_id=session_id,
        project_name=project_name,
    )

    try:
        # Create monitoring decorator
        decorated_client = LLMMonitoringDecorator(client, config)

        # Set up Kafka event handler if Kafka is available and enabled
        if config.enable_trace_collection:
            _setup_kafka_event_handler(decorated_client, config)

        return decorated_client

    except Exception as e:
        warnings.warn(f"Failed to setup monitoring: {e}", UserWarning)
        return client  # Return original client if monitoring fails


def _setup_kafka_event_handler(
    decorated_client: LLMMonitoringDecorator, config: MonitorConfig
):
    """Set up Kafka event handler for streaming events."""
    try:
        from ..kafka.producer import KafkaTraceProducer
        from ..kafka.schemas import LLMCallEvent

        # Create Kafka producer
        kafka_producer = KafkaTraceProducer(
            bootstrap_servers=config.kafka_bootstrap_servers,
            topic=config.kafka_topic,
            kafka_username=config.kafka_username,
            kafka_password=config.kafka_password,
            security_protocol=config.kafka_security_protocol,
            sasl_mechanism=config.kafka_sasl_mechanism,
        )

        # Get event system from decorator
        event_system = decorated_client.get_event_system()

        # Subscribe to LLM events
        def handle_llm_start(event_data):
            try:
                kafka_producer.send_llm_start(
                    call_id=event_data["metadata"]["call_id"],
                    model=event_data["metadata"]["model"] or "unknown",
                    provider=event_data["metadata"]["provider"],
                    messages=[],  # Simplified for privacy
                    user_id=event_data["metadata"]["user_id"],
                    session_id=event_data["metadata"]["session_id"],
                    project_name=event_data["metadata"]["project_name"],
                )
            except Exception as e:
                # Don't let Kafka errors break the main flow
                pass

        def handle_llm_end(event_data):
            try:
                metadata = event_data["metadata"]
                usage = metadata.get("usage", {})

                kafka_producer.send_llm_end(
                    call_id=metadata["call_id"],
                    model=metadata["model"] or "unknown",
                    provider=metadata["provider"],
                    duration_ms=metadata["duration_ms"],
                    usage=usage,
                    user_id=metadata["user_id"],
                    session_id=metadata["session_id"],
                    project_name=metadata["project_name"],
                )
            except Exception as e:
                # Don't let Kafka errors break the main flow
                pass

        event_system.subscribe("llm_call_start", handle_llm_start)
        event_system.subscribe("llm_call_end", handle_llm_end)

    except ImportError:
        # Kafka not available, skip event streaming
        pass
    except Exception as e:
        # Other errors, log but don't fail
        import logging

        logger = logging.getLogger(__name__)
        logger.warning(f"Failed to setup Kafka event handler: {e}")


# Legacy compatibility wrapper
def monitor_with_legacy_support(
    client: Any, provider: Optional[str] = None, **kwargs
) -> Any:
    """
    Monitor function with full legacy support.

    This function maintains 100% backward compatibility with the original
    monitor() function while using the new design patterns internally.
    """
    # Check if this is the old API usage
    if isinstance(client, str):
        # Old API: monitor(provider, client)
        warnings.warn(
            "Deprecated API usage: monitor(provider, client). Use monitor(client, provider=...) instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        provider, client = client, provider

    return enhanced_monitor(client, provider=provider, **kwargs)
