"""
APC Helper Modules

This package contains helper utilities for APC, including:
- LLM integrations (Azure OpenAI, Anthropic, Google Gemini, etc.)
- Enhanced logging with streaming support
- Utility functions for common tasks
"""

# Import logging functions directly (they will be available when helpers is imported)
try:
    from .logging import (
        setup_apc_logging,
        get_logger,
        StructuredLogger,
        stream_llm_response,
        log_llm_start,
        log_llm_complete
    )
    _has_logging = True
except ImportError:
    _has_logging = False

__all__ = []

if _has_logging:
    __all__.extend([
        'setup_apc_logging',
        'get_logger', 
        'StructuredLogger',
        'stream_llm_response',
        'log_llm_start',
        'log_llm_complete'
    ])
