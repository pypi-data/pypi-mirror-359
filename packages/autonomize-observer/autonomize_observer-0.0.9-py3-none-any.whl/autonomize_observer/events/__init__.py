"""
Event system module implementing Observer pattern.

This module provides centralized event management for observability
events throughout the SDK.
"""

from .system import EventSystem, get_global_event_system, reset_global_event_system

__all__ = [
    "EventSystem",
    "get_global_event_system",
    "reset_global_event_system",
]
