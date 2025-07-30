"""
Base LLM Client for APC

Provides a unified interface for all LLM providers with streaming support.
"""
import time
from abc import ABC, abstractmethod
from typing import Dict, List, Iterator, Optional, Any
from ..logging import get_logger, log_llm_start, log_llm_complete, stream_llm_response

class BaseLLMClient(ABC):
    """
    Base class for all LLM clients in APC.
    
    Provides:
    - Unified interface for different LLM providers
    - Automatic streaming with colored terminal output
    - Logging and performance tracking
    - Error handling and retries
    """
    
    def __init__(self, model_name: str, **kwargs):
        self.model_name = model_name
        self.logger = get_logger(f'llm.{self.__class__.__name__.lower()}')
        self._configure(**kwargs)
    
    @abstractmethod
    def _configure(self, **kwargs):
        """Configure the specific LLM client (API keys, endpoints, etc.)"""
        pass
    
    @abstractmethod
    def _create_streaming_completion(self, messages: List[Dict[str, str]], **kwargs) -> Iterator[str]:
        """Create a streaming completion request (provider-specific implementation)"""
        pass
    
    def chat_completion_streaming(self, 
                                agent_name: str,
                                messages: List[Dict[str, str]], 
                                max_tokens: int = 500,
                                temperature: float = 0.7,
                                **kwargs) -> str:
        """
        Get streaming chat completion with colored terminal output.
        
        Args:
            agent_name: Name of the agent making the request
            messages: Chat messages in OpenAI format
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            **kwargs: Provider-specific parameters
        
        Returns:
            Complete response text
        """
        start_time = time.time()
        
        # Log the start of the request
        prompt_preview = messages[-1].get('content', '') if messages else ''
        log_llm_start(agent_name, self.model_name, prompt_preview, self.logger)
        
        try:
            # Create streaming response generator
            response_generator = self._create_streaming_completion(
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                **kwargs
            )
            
            # Stream response with colored output
            full_response = stream_llm_response(
                agent_name=agent_name,
                model_name=self.model_name,
                response_generator=response_generator,
                logger=self.logger
            )
            
            duration = time.time() - start_time
            
            # Log completion
            log_llm_complete(agent_name, self.model_name, len(full_response), duration, self.logger)
            
            return full_response
            
        except Exception as e:
            duration = time.time() - start_time
            self.logger.error(f"LLM completion failed for {agent_name}: {str(e)}")
            raise
    
    def chat_completion(self, 
                       messages: List[Dict[str, str]], 
                       max_tokens: int = 500,
                       temperature: float = 0.7,
                       **kwargs) -> str:
        """
        Non-streaming chat completion (fallback method).
        
        This method should be overridden by providers if they have
        optimized non-streaming implementations.
        """
        # Use streaming but don't show streaming output
        try:
            response_generator = self._create_streaming_completion(
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                **kwargs
            )
            return ''.join(response_generator)
        except Exception as e:
            self.logger.error(f"LLM completion failed: {str(e)}")
            return f"API Error: {str(e)}"
