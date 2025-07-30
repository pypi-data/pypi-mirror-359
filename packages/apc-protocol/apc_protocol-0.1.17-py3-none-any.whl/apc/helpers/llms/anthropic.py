"""
Anthropic Claude Streaming Client for APC

Future implementation for Anthropic Claude with streaming support.
"""
from typing import Dict, List, Iterator
from .base import BaseLLMClient

class AnthropicStreamingClient(BaseLLMClient):
    """
    Anthropic Claude client with streaming support.
    
    TODO: Implement streaming Claude integration
    """
    
    def _configure(self, **kwargs):
        """Configure Anthropic client"""
        # TODO: Implement Anthropic configuration
        raise NotImplementedError("Anthropic streaming client coming soon!")
    
    def _create_streaming_completion(self, messages: List[Dict[str, str]], **kwargs) -> Iterator[str]:
        """Create streaming completion using Anthropic Claude"""
        # TODO: Implement Anthropic streaming
        raise NotImplementedError("Anthropic streaming client coming soon!")
