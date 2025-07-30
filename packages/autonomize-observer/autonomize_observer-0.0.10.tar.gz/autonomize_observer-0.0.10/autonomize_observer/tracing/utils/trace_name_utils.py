"""
Trace name utilities for cleaning and normalizing trace names.

This module provides utilities for cleaning trace names to ensure
consistent and readable trace identification.
"""


def clean_trace_name(trace_name: str) -> str:
    """
    Clean up trace name for better readability using robust generic patterns.

    Args:
        trace_name: Raw trace name to clean

    Returns:
        Cleaned trace name
    """
    if not trace_name:
        return "AgentExecutor"

    # Handle generic/untitled flows
    if trace_name.startswith("Untitled") or trace_name.lower() in [
        "untitled",
        "new flow",
        "flow",
    ]:
        return "AgentExecutor"

    # Clean up the trace name
    cleaned = trace_name.strip()

    # Remove UUID suffix pattern (e.g., "MyFlow - 597cd666-9580-462a-8ffa-b9939b6df0f0")
    if " - " in cleaned and len(cleaned.split(" - ")[-1]) >= 30:
        cleaned = cleaned.split(" - ")[0].strip()

    # Remove common document patterns
    if cleaned.endswith(")") and "(" in cleaned:
        # Handle patterns like "Untitled document (2)"
        base_name = cleaned.split("(")[0].strip()
        if base_name.lower() in ["untitled document", "untitled", "document"]:
            return "AgentExecutor"
        if base_name:
            cleaned = base_name

    # If still generic after cleaning, use AgentExecutor
    if not cleaned or cleaned.lower() in ["untitled", "document", "new", "flow"]:
        return "AgentExecutor"

    return cleaned
