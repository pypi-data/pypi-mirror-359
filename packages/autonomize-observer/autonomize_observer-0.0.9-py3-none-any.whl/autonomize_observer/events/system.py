"""
Event system implementation using Observer pattern.

This module provides a centralized event system for publishing and
subscribing to observability events throughout the SDK.
"""

import threading
from collections import defaultdict
from typing import Any, Callable, Dict, List
import logging

logger = logging.getLogger(__name__)


class EventSystem:
    """
    Centralized event system implementing the Observer pattern.

    This class manages event publishing and subscription for observability
    events throughout the SDK, enabling loose coupling between components.
    """

    def __init__(self):
        """Initialize the event system."""
        self._subscribers: Dict[str, List[Callable]] = defaultdict(list)
        self._lock = threading.RLock()

        # Statistics
        self._stats = {
            "events_published": 0,
            "events_failed": 0,
            "subscribers_count": 0,
        }

    def subscribe(self, event_type: str, handler: Callable[[Dict[str, Any]], None]):
        """
        Subscribe to events of a specific type.

        Args:
            event_type: Type of event to subscribe to
            handler: Function to call when event is published
        """
        with self._lock:
            self._subscribers[event_type].append(handler)
            self._stats["subscribers_count"] = sum(
                len(handlers) for handlers in self._subscribers.values()
            )

        logger.debug(f"Subscribed handler to event type: {event_type}")

    def unsubscribe(self, event_type: str, handler: Callable[[Dict[str, Any]], None]):
        """
        Unsubscribe from events of a specific type.

        Args:
            event_type: Type of event to unsubscribe from
            handler: Handler function to remove
        """
        with self._lock:
            if event_type in self._subscribers:
                try:
                    self._subscribers[event_type].remove(handler)
                    self._stats["subscribers_count"] = sum(
                        len(handlers) for handlers in self._subscribers.values()
                    )
                    logger.debug(f"Unsubscribed handler from event type: {event_type}")
                except ValueError:
                    logger.warning(f"Handler not found for event type: {event_type}")

    def publish(self, event_type: str, event_data: Dict[str, Any]):
        """
        Publish an event to all subscribers.

        Args:
            event_type: Type of event being published
            event_data: Event data to send to subscribers
        """
        with self._lock:
            handlers = self._subscribers.get(event_type, []).copy()

        if not handlers:
            logger.debug(f"No subscribers for event type: {event_type}")
            return

        # Publish to all handlers
        failed_handlers = []
        for handler in handlers:
            try:
                handler(event_data)
            except Exception as e:
                logger.error(f"Event handler failed for {event_type}: {e}")
                failed_handlers.append(handler)
                self._stats["events_failed"] += 1

        # Remove failed handlers to prevent repeated failures
        if failed_handlers:
            with self._lock:
                for handler in failed_handlers:
                    try:
                        self._subscribers[event_type].remove(handler)
                    except ValueError:
                        pass  # Handler already removed

        self._stats["events_published"] += 1
        logger.debug(f"Published event {event_type} to {len(handlers)} handlers")

    def publish_async(self, event_type: str, event_data: Dict[str, Any]):
        """
        Publish an event asynchronously (non-blocking).

        Args:
            event_type: Type of event being published
            event_data: Event data to send to subscribers
        """
        import concurrent.futures

        # Use thread pool for async publishing
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            executor.submit(self.publish, event_type, event_data)

    def clear_subscribers(self, event_type: str = None):
        """
        Clear subscribers for a specific event type or all event types.

        Args:
            event_type: Specific event type to clear, or None for all
        """
        with self._lock:
            if event_type:
                if event_type in self._subscribers:
                    del self._subscribers[event_type]
                    logger.debug(f"Cleared subscribers for event type: {event_type}")
            else:
                self._subscribers.clear()
                logger.debug("Cleared all event subscribers")

            self._stats["subscribers_count"] = sum(
                len(handlers) for handlers in self._subscribers.values()
            )

    def get_stats(self) -> Dict[str, Any]:
        """Get event system statistics."""
        with self._lock:
            return {
                "events_published": self._stats["events_published"],
                "events_failed": self._stats["events_failed"],
                "subscribers_count": self._stats["subscribers_count"],
                "event_types": list(self._subscribers.keys()),
                "subscribers_by_type": {
                    event_type: len(handlers)
                    for event_type, handlers in self._subscribers.items()
                },
            }

    def reset_stats(self):
        """Reset event system statistics."""
        with self._lock:
            self._stats["events_published"] = 0
            self._stats["events_failed"] = 0


# Global event system instance
_global_event_system: EventSystem = None
_event_system_lock = threading.Lock()


def get_global_event_system() -> EventSystem:
    """Get or create the global event system instance."""
    global _global_event_system

    if _global_event_system is None:
        with _event_system_lock:
            if _global_event_system is None:
                _global_event_system = EventSystem()

    return _global_event_system


def reset_global_event_system():
    """Reset the global event system (mainly for testing)."""
    global _global_event_system

    with _event_system_lock:
        _global_event_system = None
