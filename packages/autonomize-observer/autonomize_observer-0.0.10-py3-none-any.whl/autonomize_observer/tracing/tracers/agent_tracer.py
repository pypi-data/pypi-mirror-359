"""
Streaming Agent-based tracer inspired by Langflow's approach.

This tracer implements streaming/incremental span sending:
1. Start trace context
2. Send individual spans as they start/end
3. No massive memory accumulation
4. Real-time monitoring capabilities
"""

import logging
import time
import uuid
from contextlib import contextmanager
from typing import Any, Dict, List, Optional

from ...kafka.producer import KafkaTraceProducer
from ...kafka.schemas import _safe_serialize_value
from ..utils.model_utils import (
    clean_model_name,
    guess_provider_from_model,
    infer_component_type,
)
from ..utils.trace_name_utils import clean_trace_name
from .base_tracer import BaseTracer
from .trace_context import StreamingTraceContext

# Streaming tracer is lightweight - no heavy dependencies
COST_TRACKING_AVAILABLE = False  # Cost calculation happens in worker

try:
    from ..callbacks.langchain_callback import (
        LANGCHAIN_AVAILABLE,
        StreamingLangChainCallback,
    )
except ImportError:
    LANGCHAIN_AVAILABLE = False
    StreamingLangChainCallback = None

logger = logging.getLogger(__name__)


class AgentTracer(BaseTracer):
    """
    Streaming Agent tracer that sends spans incrementally like Langflow.

    Workflow:
    1. start_trace() - Initialize trace context, send trace_start event
    2. add_trace() - Start component span, send span_start event
    3. end_trace() - End component span, send span_end event
    4. end() - Finalize trace, send trace_end event
    """

    def __init__(
        self,
        trace_name: str,
        trace_id: uuid.UUID,
        flow_id: str,
        project_name: str = "GenesisStudio",
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        kafka_bootstrap_servers: Optional[str] = None,
        kafka_topic: str = "genesis-traces-streaming",
        # Authentication parameters
        kafka_username: Optional[str] = None,
        kafka_password: Optional[str] = None,
        security_protocol: str = "PLAINTEXT",
        sasl_mechanism: str = "PLAIN",
        **kwargs,
    ):
        """Initialize streaming tracer."""
        # Clean up trace name using robust generic approach
        cleaned_trace_name = clean_trace_name(trace_name)
        super().__init__(cleaned_trace_name, "flow", project_name, trace_id)

        # Store configuration
        self.flow_id = flow_id
        self.user_id = user_id
        self.session_id = session_id

        # Kafka configuration
        self.kafka_bootstrap_servers = kafka_bootstrap_servers
        self.kafka_topic = kafka_topic
        self.kafka_username = kafka_username
        self.kafka_password = kafka_password
        self.security_protocol = security_protocol
        self.sasl_mechanism = sasl_mechanism

        # Initialize Kafka producer
        self._kafka_producer = None
        self._ready = False

        # Trace context (like Langflow's TraceContext)
        self._trace_context: Optional[StreamingTraceContext] = None

        # LangChain callback
        self._callback_handler = None
        if LANGCHAIN_AVAILABLE:
            self._callback_handler = StreamingLangChainCallback(self)

        # Setup Kafka producer
        self._setup_kafka_producer()

        logger.info(f"✅ Streaming tracer initialized for flow: {flow_id}")

    @property
    def ready(self) -> bool:
        """Check if tracer is ready."""
        return self._ready

    def _setup_kafka_producer(self):
        """Setup Kafka producer with authentication."""
        try:
            self._kafka_producer = KafkaTraceProducer(
                bootstrap_servers=self.kafka_bootstrap_servers,
                topic=self.kafka_topic,
                kafka_username=self.kafka_username,
                kafka_password=self.kafka_password,
                security_protocol=self.security_protocol,
                sasl_mechanism=self.sasl_mechanism,
            )
            self._ready = True
            logger.debug("✅ Streaming Kafka producer initialized")
        except Exception as e:
            logger.warning(f"❌ Failed to initialize Kafka producer: {e}")
            self._ready = False

    def start_trace(self) -> None:
        """
        Start the trace context and send trace_start event.

        This is like Langflow's start_tracers().
        """
        if not self._ready:
            logger.debug("Streaming tracer not ready, skipping trace start")
            return

        try:
            # Initialize trace context
            self._trace_context = StreamingTraceContext(
                trace_id=str(self.trace_id),
                flow_id=self.flow_id,
                trace_name=self.trace_name,
                project_name=self.project_name,
                user_id=self.user_id,
                session_id=self.session_id,
            )

            # Send trace_start event to Kafka using specific method
            success = self._kafka_producer.send_trace_start(
                trace_id=self._trace_context.trace_id,
                flow_id=self._trace_context.flow_id,
                flow_name=self._trace_context.trace_name,
                user_id=self._trace_context.user_id,
                session_id=self._trace_context.session_id,
                metadata={
                    "project_name": self._trace_context.project_name,
                    "environment": "production",
                },
            )
            if success:
                logger.info(
                    f"✅ Started streaming trace: {self._trace_context.trace_id}"
                )
            else:
                logger.warning(f"❌ Failed to send trace_start event")

        except Exception as e:
            logger.error(f"Error starting streaming trace: {e}")

    def add_trace(
        self,
        trace_id: str,  # component_id
        trace_name: str,
        trace_type: str,
        inputs: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None,
        vertex: Any = None,
        parent_id: Optional[str] = None,
    ) -> None:
        """
        Start a component span and send span_start event.

        This is like Langflow's add_trace() for individual components.
        """
        if not self._ready or not self._trace_context:
            return

        try:
            # Create span info
            span_start_time = time.time()
            safe_inputs = _safe_serialize_value(inputs) if inputs else {}
            safe_metadata = _safe_serialize_value(metadata) if metadata else {}

            # Store active span using context method
            span_info = {
                "span_id": trace_id,
                "component_name": trace_name,
                "trace_type": trace_type,
                "start_time": span_start_time,
                "inputs": safe_inputs,
                "metadata": safe_metadata,
                "parent_id": parent_id,
            }
            self._trace_context.add_span(trace_id, span_info)

            # Send span_start event to Kafka using specific method
            success = self._kafka_producer.send_span_start(
                trace_id=self._trace_context.trace_id,
                span_id=trace_id,
                component_id=trace_id,  # Use span_id as component_id
                component_name=trace_name,
                parent_span_id=parent_id,
                input_data=safe_inputs,
                metadata=safe_metadata,
            )
            if success:
                logger.debug(f"✅ Started span: {trace_id} ({trace_name})")
            else:
                logger.warning(f"❌ Failed to send span_start event for {trace_id}")

        except Exception as e:
            logger.error(f"Error starting span {trace_id}: {e}")

    def end_trace(
        self,
        trace_id: str,
        trace_name: str,
        outputs: Optional[Dict[str, Any]] = None,
        error: Optional[Exception] = None,
        logs: Any = (),
    ):
        """
        End a component span and send span_end event.

        This is like Langflow's end_trace() for individual components.
        """
        if not self._ready or not self._trace_context:
            return

        try:
            span_end_time = time.time()
            safe_outputs = _safe_serialize_value(outputs) if outputs else {}

            # Get span info and mark as completed using context method
            span_info = self._trace_context.complete_span(trace_id)

            if not span_info:
                logger.warning(f"Trying to end unknown span: {trace_id}")
                return

            # Calculate duration
            duration_ms = (span_end_time - span_info["start_time"]) * 1000

            # Lightweight metadata - worker handles cost calculation
            enhanced_metadata = {
                "component_name": trace_name,
                "status": "error" if error else "success",
                "component_type": infer_component_type(trace_name, None),
            }

            # Send span_end event to Kafka using specific method
            success = self._kafka_producer.send_span_end(
                trace_id=self._trace_context.trace_id,
                span_id=trace_id,
                duration_ms=duration_ms,
                output_data=safe_outputs,
                metadata=enhanced_metadata,
                error=str(error) if error else None,
            )
            if success:
                logger.debug(
                    f"✅ Ended span: {trace_id} (duration: {duration_ms:.2f}ms)"
                )
            else:
                logger.warning(f"❌ Failed to send span_end event for {trace_id}")

        except Exception as e:
            logger.error(f"Error ending span {trace_id}: {e}")

    def end(
        self,
        inputs: Dict[str, Any],
        outputs: Dict[str, Any],
        error: Optional[Exception] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        End the entire trace and send trace_end event.

        This is like Langflow's end_tracers().
        """
        if not self._ready or not self._trace_context:
            return

        try:
            trace_end_time = time.time()
            duration_ms = (trace_end_time - self._trace_context.start_time) * 1000

            # Lightweight trace metrics - worker handles cost calculation
            total_spans = self._trace_context.get_span_count()

            # Send trace_end event to Kafka (lightweight)
            trace_metadata = {
                "flow_id": self._trace_context.flow_id,
                "trace_name": self._trace_context.trace_name,
                "total_spans": total_spans,
                "status": "error" if error else "success",
                "project_name": getattr(
                    self._trace_context, "project_name", "GenesisStudio"
                ),
                **self._trace_context.tags,
                **self._trace_context.params,
                **self._trace_context.metrics,
                **(metadata or {}),
            }

            success = self._kafka_producer.send_trace_end(
                trace_id=self._trace_context.trace_id,
                duration_ms=duration_ms,
                metadata=trace_metadata,
                error=str(error) if error else None,
            )
            if success:
                logger.info(
                    f"✅ Completed streaming trace: {self._trace_context.trace_id} "
                    f"(duration: {duration_ms:.2f}ms, spans: {total_spans})"
                )
            else:
                logger.warning(f"❌ Failed to send trace_end event")

            # Flush any pending messages
            self._flush_producer()

        except Exception as e:
            logger.error(f"Error ending streaming trace: {e}")

    def add_cost_event(self, event_data: Dict[str, Any]) -> None:
        """Lightweight cost event tracking - worker handles calculation."""
        # In streaming mode, cost calculation is done by worker
        # Just log for debugging purposes
        logger.debug(
            f"Cost event data sent to worker: {event_data.get('model_name', 'unknown')}"
        )

    def add_tags(self, tags: Dict[str, str]):
        """Add tags to trace context."""
        if self._trace_context:
            self._trace_context.update_tags(tags)

    def log_param(self, key: str, value: Any):
        """Log parameter to trace context."""
        if self._trace_context:
            self._trace_context.set_param(key, value)

    def log_metric(self, key: str, value: float):
        """Log metric to trace context."""
        if self._trace_context:
            self._trace_context.set_metric(key, value)

    def get_langchain_callback(self):
        """Get LangChain callback handler."""
        return self._callback_handler

    def _flush_producer(self):
        """Flush Kafka producer."""
        try:
            if self._kafka_producer:
                pending = self._kafka_producer.flush(timeout=5.0)
                if pending > 0:
                    logger.warning(f"{pending} messages still pending after flush")
        except Exception as e:
            logger.error(f"Error flushing producer: {e}")

    def close(self):
        """Close the tracer."""
        try:
            self._flush_producer()
            if self._kafka_producer:
                self._kafka_producer.close()
                self._kafka_producer = None
            logger.debug("Streaming tracer closed")
        except Exception as e:
            logger.error(f"Error closing streaming tracer: {e}")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - ensure cleanup."""
        self.close()
        return False

    def __del__(self):
        """Destructor to ensure cleanup."""
        self.close()


# Context manager for easy usage
@contextmanager
def streaming_trace(trace_name: str, trace_id: uuid.UUID, flow_id: str, **kwargs):
    """
    Context manager for streaming traces.

    Usage:
        with streaming_trace("My Flow", trace_id, flow_id) as tracer:
            tracer.add_trace("comp1", "Component 1", "llm", inputs)
            # ... do work ...
            tracer.end_trace("comp1", "Component 1", outputs)
    """
    tracer = AgentTracer(
        trace_name=trace_name, trace_id=trace_id, flow_id=flow_id, **kwargs
    )

    try:
        tracer.start_trace()
        yield tracer
    except Exception as e:
        tracer.end({}, {}, error=e)
        raise
    else:
        tracer.end({}, {})
    finally:
        tracer.close()
