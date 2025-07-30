"""Callback implementations for various frameworks."""

try:
    from .langchain_callback import LANGCHAIN_AVAILABLE, StreamingLangChainCallback

    _has_langchain = True
except ImportError:
    _has_langchain = False
    StreamingLangChainCallback = None
    LANGCHAIN_AVAILABLE = False

__all__ = ["LANGCHAIN_AVAILABLE"]

if _has_langchain:
    __all__.extend(["StreamingLangChainCallback"])
