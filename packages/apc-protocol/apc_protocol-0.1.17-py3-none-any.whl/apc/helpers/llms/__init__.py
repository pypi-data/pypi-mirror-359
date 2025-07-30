"""
LLM Integration Modules for APC

This package provides streaming LLM integrations with colored terminal output.
Supports multiple providers with a unified interface.
"""

try:
    from .base import BaseLLMClient
    _has_base = True
except ImportError:
    _has_base = False

try:
    from .azure_openai import AzureOpenAIStreamingClient
    _has_azure = True
except ImportError:
    _has_azure = False

__all__ = []

if _has_base:
    __all__.append('BaseLLMClient')

if _has_azure:
    __all__.append('AzureOpenAIStreamingClient')
