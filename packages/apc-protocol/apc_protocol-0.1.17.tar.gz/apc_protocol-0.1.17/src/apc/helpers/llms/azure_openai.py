"""
Azure OpenAI Streaming Client for APC

Provides streaming Azure OpenAI integration with colored terminal output.
"""
import os
from typing import Dict, List, Iterator, Optional
from .base import BaseLLMClient

class AzureOpenAIStreamingClient(BaseLLMClient):
    """
    Azure OpenAI client with streaming support and colored terminal output.
    
    Automatically streams responses in purple/violet colors and provides
    real-time feedback during LLM generation.
    """
    
    def __init__(self, **kwargs):
        # Initialize with default model name, will be updated in _configure
        super().__init__(model_name="azure-openai", **kwargs)
    
    def _configure(self, **kwargs):
        """Configure Azure OpenAI client with automatic environment variable detection"""
        try:
            from openai import AzureOpenAI
        except ImportError:
            raise ImportError(
                "Azure OpenAI integration requires the OpenAI package.\n"
                "Install with: pip install openai"
            )
        
        # Automatically load from environment variables (.env file) if not provided in kwargs
        self.api_key = kwargs.get('api_key') or os.getenv("AZURE_OPENAI_API_KEY")
        self.endpoint = kwargs.get('endpoint') or os.getenv("AZURE_OPENAI_ENDPOINT") 
        self.api_version = kwargs.get('api_version') or os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
        self.deployment_name = kwargs.get('deployment_name') or os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
        
        # Validate required configuration with detailed error messages
        if not all([self.api_key, self.endpoint, self.deployment_name]):
            missing = []
            if not self.api_key:
                missing.append("AZURE_OPENAI_API_KEY")
            if not self.endpoint:
                missing.append("AZURE_OPENAI_ENDPOINT")
            if not self.deployment_name:
                missing.append("AZURE_OPENAI_DEPLOYMENT_NAME")
            
            raise ValueError(
                f"❌ Missing Azure OpenAI configuration: {', '.join(missing)}\n\n"
                "🔧 Add these environment variables to your .env file:\n"
                f"AZURE_OPENAI_API_KEY=your_api_key_here\n"
                f"AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/\n"
                f"AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4\n"
                f"AZURE_OPENAI_API_VERSION=2024-02-15-preview  # Optional, defaults to this\n\n"
                "💡 Copy .env.example to .env and fill in your Azure OpenAI credentials."
            )
        
        # Initialize Azure OpenAI client
        try:
            self.client = AzureOpenAI(
                api_key=self.api_key,
                api_version=self.api_version,
                azure_endpoint=self.endpoint
            )
        except Exception as e:
            raise ValueError(
                f"❌ Failed to initialize Azure OpenAI client: {str(e)}\n"
                "🔧 Check your .env file configuration:\n"
                f"   Endpoint: {self.endpoint}\n"
                f"   Deployment: {self.deployment_name}\n"
                f"   API Version: {self.api_version}"
            )
        
        # Update model name to include deployment info for better logging
        self.model_name = f"{self.deployment_name} (Azure OpenAI)"
        
        # Log successful configuration (without sensitive data)
        clean_endpoint = self.endpoint.split('//')[1] if '//' in self.endpoint else self.endpoint
        self.logger.info(f"Azure OpenAI client configured: {self.deployment_name} @ {clean_endpoint}")
    
    def _create_streaming_completion(self, messages: List[Dict[str, str]], **kwargs) -> Iterator[str]:
        """Create streaming completion using Azure OpenAI"""
        try:
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=messages,
                max_tokens=kwargs.get('max_tokens', 500),
                temperature=kwargs.get('temperature', 0.7),
                stream=True  # Enable streaming
            )
            
            for chunk in response:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            self.logger.error(f"Azure OpenAI streaming error: {str(e)}")
            yield f"API Error: {str(e)}"
    
    def chat_completion(self, messages: List[Dict[str, str]], max_tokens: int = 500, temperature: float = 0.7) -> str:
        """
        Non-streaming chat completion for Azure OpenAI.
        
        This is optimized for cases where streaming is not needed.
        """
        try:
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                stream=False  # No streaming
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            self.logger.error(f"Azure OpenAI API Error: {str(e)}")
            return f"API Error: {str(e)}"
    
    @classmethod
    def check_configuration(cls) -> dict:
        """
        Check Azure OpenAI configuration without initializing the client.
        
        Returns:
            Dict with configuration status and any missing variables
        """
        config = {
            "api_key": bool(os.getenv("AZURE_OPENAI_API_KEY")),
            "endpoint": bool(os.getenv("AZURE_OPENAI_ENDPOINT")),
            "deployment_name": bool(os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")),
            "api_version": os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
        }
        
        missing = [key.replace('_', ' ').upper() for key, value in config.items() 
                  if key != 'api_version' and not value]
        
        return {
            "configured": len(missing) == 0,
            "missing_vars": missing,
            "endpoint": os.getenv("AZURE_OPENAI_ENDPOINT", "Not set"),
            "deployment": os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "Not set"),
            "api_version": config["api_version"]
        }
    
    @classmethod
    def test_configuration(cls) -> bool:
        """
        Test Azure OpenAI configuration and connection.
        
        Returns:
            bool: True if configuration is valid and connection works
        """
        try:
            # Check configuration
            status = cls.check_configuration()
            if not status['configured']:
                print(f"❌ Configuration incomplete. Missing: {', '.join(status['missing_vars'])}")
                return False
            
            print("✅ Configuration found")
            print(f"🌐 Endpoint: {status['endpoint']}")
            print(f"🚀 Deployment: {status['deployment']}")
            
            # Test connection
            client = cls()
            test_response = client.chat_completion(
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=10
            )
            
            if "API Error" not in test_response:
                print("✅ Connection test successful")
                return True
            else:
                print(f"❌ Connection test failed: {test_response}")
                return False
                
        except Exception as e:
            print(f"❌ Configuration test failed: {str(e)}")
            return False
