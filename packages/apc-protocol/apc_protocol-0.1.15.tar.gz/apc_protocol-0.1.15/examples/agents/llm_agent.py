"""
LLM Agent Example
Demonstrates integration with Large Language Models for AI-powered tasks.
"""
import asyncio
import json
from typing import Dict, Any, List, Optional
from apc import Worker
from apc.transport import GRPCTransport

class LLMAgent:
    """
    AI-powered agent using Large Language Models.
    
    Capabilities:
    - Text generation and completion
    - Question answering
    - Content summarization
    - Translation
    - Code generation
    """
    
    def __init__(self, worker_id: str = "llm-agent-001", model: str = "gpt-3.5-turbo"):
        self.worker = Worker(
            worker_id=worker_id,
            roles=["text-generator", "qa-assistant", "translator", "code-generator"]
        )
        self.transport = GRPCTransport(port=50054)
        self.worker.bind_transport(self.transport)
        self.model = model
        
        # Register handlers
        self._register_handlers()
    
    def _register_handlers(self):
        """Register all LLM-based handlers."""
        
        @self.worker.register_handler("generate_text")
        async def generate_text(params: Dict[str, Any]) -> Dict[str, Any]:
            """Generate text based on a prompt."""
            prompt = params.get("prompt")
            max_tokens = params.get("max_tokens", 150)
            temperature = params.get("temperature", 0.7)
            
            if not prompt:
                raise ValueError("prompt parameter is required")
            
            # Simulate LLM API call
            await asyncio.sleep(1.5)
            
            # Mock response
            generated_text = f"This is a generated response to: '{prompt[:50]}...'"
            
            return {
                "status": "success",
                "generated_text": generated_text,
                "model": self.model,
                "tokens_used": max_tokens,
                "finish_reason": "stop"
            }
        
        @self.worker.register_handler("answer_question")
        async def answer_question(params: Dict[str, Any]) -> Dict[str, Any]:
            """Answer questions based on context."""
            question = params.get("question")
            context = params.get("context", "")
            
            if not question:
                raise ValueError("question parameter is required")
            
            # Simulate processing
            await asyncio.sleep(1.0)
            
            return {
                "status": "success",
                "question": question,
                "answer": f"Based on the provided context, the answer is: [Generated answer for '{question}']",
                "confidence": 0.85,
                "sources": ["context_provided"]
            }
        
        @self.worker.register_handler("summarize_text")
        async def summarize_text(params: Dict[str, Any]) -> Dict[str, Any]:
            """Summarize long text content."""
            text = params.get("text")
            max_length = params.get("max_length", 100)
            
            if not text:
                raise ValueError("text parameter is required")
            
            # Simulate summarization
            await asyncio.sleep(0.8)
            
            return {
                "status": "success",
                "original_length": len(text),
                "summary": f"Summary of the provided text (max {max_length} words): Key points include...",
                "compression_ratio": 0.25
            }
        
        @self.worker.register_handler("translate_text")
        async def translate_text(params: Dict[str, Any]) -> Dict[str, Any]:
            """Translate text between languages."""
            text = params.get("text")
            source_lang = params.get("source_language", "auto")
            target_lang = params.get("target_language")
            
            if not text or not target_lang:
                raise ValueError("text and target_language parameters are required")
            
            # Simulate translation
            await asyncio.sleep(1.2)
            
            return {
                "status": "success",
                "original_text": text,
                "translated_text": f"[Translated to {target_lang}]: {text}",
                "source_language": source_lang,
                "target_language": target_lang,
                "confidence": 0.92
            }
        
        @self.worker.register_handler("generate_code")
        async def generate_code(params: Dict[str, Any]) -> Dict[str, Any]:
            """Generate code based on natural language description."""
            description = params.get("description")
            language = params.get("language", "python")
            
            if not description:
                raise ValueError("description parameter is required")
            
            # Simulate code generation
            await asyncio.sleep(2.0)
            
            code_template = f"""
# Generated {language} code for: {description}
def generated_function():
    \"\"\"
    {description}
    \"\"\"
    # Implementation would go here
    return "Generated result"

# Example usage
result = generated_function()
print(result)
"""
            
            return {
                "status": "success",
                "description": description,
                "language": language,
                "generated_code": code_template.strip(),
                "explanation": f"This {language} code implements: {description}"
            }
    
    async def start(self):
        """Start the LLM agent."""
        print("🤖 Starting LLM Agent...")
        await self.worker.start()
        await self.transport.start_server()
        print(f"✅ LLM Agent running on port 50054")
        print(f"🧠 Model: {self.model}")
        print(f"🔧 Available capabilities: {list(self.worker.roles)}")
    
    async def stop(self):
        """Stop the LLM agent."""
        await self.transport.stop_server()
        await self.worker.stop()
        print("🛑 LLM Agent stopped")

async def main():
    """Run the LLM agent."""
    agent = LLMAgent()
    
    try:
        await agent.start()
        
        # Keep running
        print("💡 Agent is ready to receive AI tasks...")
        print("   Available handlers:")
        print("   • generate_text - Generate text from prompts")
        print("   • answer_question - Answer questions with context")
        print("   • summarize_text - Summarize long content")
        print("   • translate_text - Translate between languages")
        print("   • generate_code - Generate code from descriptions")
        print("\n   Ctrl+C to stop")
        
        while True:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        print("\n⏹️  Shutting down...")
    finally:
        await agent.stop()

if __name__ == "__main__":
    asyncio.run(main())
