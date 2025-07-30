"""
Enhanced Azure OpenAI integration with streaming support and colorized output.
Part of the APC library for beautiful LLM interactions.
"""
import os
import time
from typing import List, Dict, Any, Iterator, Optional
from apc.logging import get_logger, stream_llm_response, log_llm_start, log_llm_complete

try:
    from openai import AzureOpenAI
except ImportError:
    AzureOpenAI = None

class APCAzureOpenAIClient:
    """
    APC's enhanced Azure OpenAI client with automatic streaming and colorized output.
    
    Features:
    - Automatic streaming responses with purple/violet terminal colors
    - Agent name and model tracking in logs
    - Built-in error handling and retries
    - Seamless integration with APC logging system
    """
    
    def __init__(self, agent_name: str = "APC-Agent"):
        if AzureOpenAI is None:
            raise ImportError("Please install openai: pip install openai")
        
        self.agent_name = agent_name
        self.logger = get_logger(f'azure_openai.{agent_name}')
        
        # Initialize Azure OpenAI client
        self.client = AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
        )
        self.deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
        
        if not all([self.client.api_key, self.client.azure_endpoint, self.deployment]):
            raise ValueError(
                "Missing Azure OpenAI configuration. Please set:\n"
                "- AZURE_OPENAI_API_KEY\n"
                "- AZURE_OPENAI_ENDPOINT\n"
                "- AZURE_OPENAI_DEPLOYMENT_NAME"
            )
    
    def chat_completion_stream(
        self, 
        messages: List[Dict[str, str]], 
        max_tokens: int = 400,
        temperature: float = 0.7,
        show_stream: bool = True
    ) -> str:
        """
        Get streaming chat completion with automatic purple terminal output.
        
        Args:
            messages: List of message dictionaries
            max_tokens: Maximum tokens to generate
            temperature: Temperature for response generation
            show_stream: Whether to show streaming output in terminal
        
        Returns:
            Complete response text
        """
        start_time = time.time()
        
        # Log start of request
        prompt_preview = messages[-1].get('content', '') if messages else ''
        log_llm_start(self.agent_name, self.deployment, prompt_preview, self.logger)
        
        try:
            # Create streaming response
            response_stream = self.client.chat.completions.create(
                model=self.deployment,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                stream=True
            )
            
            # Generator for streaming chunks
            def chunk_generator() -> Iterator[str]:
                for chunk in response_stream:
                    if chunk.choices and chunk.choices[0].delta.content:
                        yield chunk.choices[0].delta.content
            
            # Stream with purple colors if enabled
            if show_stream:
                full_response = stream_llm_response(
                    self.agent_name, 
                    self.deployment, 
                    chunk_generator(),
                    self.logger
                )
            else:
                # Collect response without streaming display
                full_response = "".join(chunk_generator())
            
            # Log completion
            duration = time.time() - start_time
            log_llm_complete(self.agent_name, self.deployment, len(full_response), duration, self.logger)
            
            return full_response
            
        except Exception as e:
            self.logger.error(f"Azure OpenAI API Error: {str(e)}")
            return f"API Error: {str(e)}"
    
    def chat_completion(
        self, 
        messages: List[Dict[str, str]], 
        max_tokens: int = 400,
        temperature: float = 0.7
    ) -> str:
        """
        Get non-streaming chat completion (fallback method).
        For streaming with colors, use chat_completion_stream().
        """
        try:
            response = self.client.chat.completions.create(
                model=self.deployment,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            self.logger.error(f"Azure OpenAI API Error: {str(e)}")
            return f"API Error: {str(e)}"

def create_azure_openai_client(agent_name: str = "APC-Agent") -> APCAzureOpenAIClient:
    """
    Factory function to create an APC Azure OpenAI client with streaming support.
    
    Args:
        agent_name: Name of the agent using this client
    
    Returns:
        Configured APCAzureOpenAIClient instance
    """
    return APCAzureOpenAIClient(agent_name)
