# 🚀 APC Protocol - Complete Usage Guide

## Overview

The APC (Agent Protocol Conductor) is now **fully functional and production-ready**! This guide shows you exactly how to use this protocol in your projects with real examples.

## 📦 Installation

### Quick Setup (Recommended)

```bash
# 1. Clone/download the project
git clone <your-repo> && cd APC

# 2. Run the automated setup
python quick_start.py
```

### Manual Setup

```bash
# 1. Create virtual environment
python -m venv .venv

# 2. Activate environment
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Install APC package
cd apc_core && pip install -e . && cd ..

# 5. Validate installation
python validate_setup.py
```

## 🎯 How to Use APC in Your Projects

### 1. Basic Conductor-Worker Pattern

```python
"""
Basic usage: Create a conductor that orchestrates workers
"""
import asyncio
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '.'))

from apc_core import Conductor, Worker
from apc_core.messages import apc_pb2, apc_pb2_grpc
from apc_core.transport.grpc import GRPCTransport

async def main():
    # 1. Create a worker with specific capabilities
    worker = Worker("data-worker")
    worker.add_capability("data-processing")
    
    # 2. Define what the worker can do
    async def process_data(task_params):
        # Your business logic here
        data = task_params.get("data", [])
        processed = [item * 2 for item in data]
        return {"processed_data": processed, "count": len(processed)}
    
    worker.register_handler("process_data", process_data)
    
    # 3. Start worker server
    await worker.start_server(port=50052)
    
    # 4. Create conductor  
    conductor = Conductor("main-conductor")
    
    # 5. Define workflow
    workflow = [
        {"step": "process_data", "params": {"data": [1, 2, 3, 4, 5]}}
    ]
    
    # 6. Execute workflow
    result = await conductor.execute_workflow("batch-001", workflow)
    print(f"Workflow result: {result}")

if __name__ == "__main__":
    asyncio.run(main())
```

### 2. Multi-Step Data Pipeline

```python
"""
Real-world example: Data processing pipeline
"""
import asyncio
from apc_core import Conductor, Worker

class DataPipelineOrchestrator:
    def __init__(self):
        self.conductor = Conductor("pipeline-conductor")
    
    async def run_pipeline(self, data_source):
        """Run a complete data processing pipeline"""
        
        # Define multi-step workflow
        workflow = [
            {
                "step": "extract_data",
                "params": {"source": data_source},
                "required_role": "data-extractor"
            },
            {
                "step": "validate_data", 
                "params": {"rules": ["not_null", "type_check"]},
                "required_role": "data-validator",
                "depends_on": ["extract_data"]
            },
            {
                "step": "transform_data",
                "params": {"format": "normalized"},
                "required_role": "data-transformer", 
                "depends_on": ["validate_data"]
            },
            {
                "step": "load_data",
                "params": {"destination": "warehouse"},
                "required_role": "data-loader",
                "depends_on": ["transform_data"]
            }
        ]
        
        # Execute the complete pipeline
        result = await self.conductor.execute_workflow("pipeline-001", workflow)
        return result

# Usage
orchestrator = DataPipelineOrchestrator()
result = await orchestrator.run_pipeline("database://source")
```

### 3. Specialized Worker Agents

```python
"""
Create specialized agents for different tasks
"""

class DataExtractionAgent:
    def __init__(self):
        self.worker = Worker("data-extractor", roles=["data-extractor"])
        
    async def setup(self):
        @self.worker.register_handler("extract_data")
        async def extract_data(params):
            source = params.get("source")
            # Your extraction logic
            return {"extracted_records": 1000, "source": source}
        
        await self.worker.start_server(port=50053)

class MLModelAgent:
    def __init__(self):
        self.worker = Worker("ml-agent", roles=["model-trainer", "predictor"])
        
    async def setup(self):
        @self.worker.register_handler("train_model")
        async def train_model(params):
            # Your ML training logic
            return {"model_id": "model_v1", "accuracy": 0.95}
        
        @self.worker.register_handler("predict")
        async def predict(params):
            # Your prediction logic
            return {"predictions": [0.8, 0.6, 0.9], "confidence": 0.85}
        
        await self.worker.start_server(port=50054)

# Start multiple specialized agents
data_agent = DataExtractionAgent()
ml_agent = MLModelAgent()

await data_agent.setup()
await ml_agent.setup()
```

### 4. LLM Integration Example

```python
"""
Integrate with Large Language Models
"""
import openai  # or your preferred LLM client

class LLMAgent:
    def __init__(self, api_key):
        self.worker = Worker("llm-agent", roles=["text-generator", "qa-assistant"])
        self.client = openai.OpenAI(api_key=api_key)
        
    async def setup(self):
        @self.worker.register_handler("generate_text")
        async def generate_text(params):
            prompt = params.get("prompt")
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}]
            )
            return {"generated_text": response.choices[0].message.content}
        
        @self.worker.register_handler("analyze_sentiment")  
        async def analyze_sentiment(params):
            text = params.get("text")
            # Your sentiment analysis logic
            return {"sentiment": "positive", "confidence": 0.89}
        
        await self.worker.start_server(port=50055)

# Usage with conductor
async def run_content_pipeline():
    conductor = Conductor("content-conductor")
    
    workflow = [
        {
            "step": "generate_text",
            "params": {"prompt": "Write a product description for a smart watch"},
            "required_role": "text-generator"
        },
        {
            "step": "analyze_sentiment",
            "params": {"text": "{{previous_result.generated_text}}"},
            "required_role": "qa-assistant",
            "depends_on": ["generate_text"]
        }
    ]
    
    result = await conductor.execute_workflow("content-001", workflow)
    return result
```

### 5. Checkpoint and Recovery

```python
"""
Use checkpoints for fault tolerance
"""
from apc_core import CheckpointManager, RedisBackend
import redis

# Setup checkpoint backend
redis_client = redis.Redis(host='localhost', port=6379)
checkpoint_mgr = CheckpointManager(RedisBackend(redis_client))

# Create conductor with checkpointing
conductor = Conductor("resilient-conductor", checkpoint_manager=checkpoint_mgr)

async def resilient_workflow():
    batch_id = "critical-batch-001"
    
    # Try to recover from previous execution
    if conductor.recover_from_checkpoint(batch_id):
        print("Resumed from checkpoint")
    else:
        print("Starting fresh workflow")
    
    # Define long-running workflow
    workflow = [
        {"step": "step1", "params": {"data": "large_dataset"}},
        {"step": "step2", "params": {"processing": "intensive"}},
        {"step": "step3", "params": {"output": "final_result"}}
    ]
    
    # Execute with automatic checkpointing
    result = await conductor.execute_workflow(batch_id, workflow)
    return result
```

### 6. Production Deployment Pattern

```python
"""
Production-ready deployment pattern
"""
import logging
import signal
import asyncio
from apc_core import Conductor, Worker
from apc_core.transport import GRPCTransport, WebSocketTransport

class ProductionAgent:
    def __init__(self, agent_id, roles, port):
        self.worker = Worker(agent_id, roles=roles)
        self.transport = GRPCTransport(port=port)
        self.worker.bind_transport(self.transport)
        self.running = False
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(agent_id)
        
    async def start(self):
        """Start the agent with graceful shutdown handling"""
        self.running = True
        
        # Register signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        try:
            await self.worker.start()
            await self.transport.start_server()
            self.logger.info(f"Agent started on port {self.transport.port}")
            
            # Keep running
            while self.running:
                await asyncio.sleep(1)
                
        except Exception as e:
            self.logger.error(f"Agent error: {e}")
        finally:
            await self.shutdown()
    
    def _signal_handler(self, signum, frame):
        self.logger.info(f"Received signal {signum}, shutting down...")
        self.running = False
    
    async def shutdown(self):
        """Graceful shutdown"""
        self.logger.info("Shutting down agent...")
        await self.transport.stop_server()
        await self.worker.stop()
        self.logger.info("Agent stopped")

# Deploy multiple agents
async def deploy_production_system():
    agents = [
        ProductionAgent("data-processor-001", ["data-processor"], 50051),
        ProductionAgent("ml-trainer-001", ["ml-trainer"], 50052),
        ProductionAgent("api-server-001", ["api-server"], 50053),
    ]
    
    # Start all agents
    tasks = [agent.start() for agent in agents]
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(deploy_production_system())
```

## 🔧 Configuration Examples

### Environment Configuration

```bash
# .env file
APC_CONDUCTOR_ID=main-conductor
APC_WORKER_ID=worker-001
APC_CHECKPOINT_BACKEND=redis
APC_REDIS_URL=redis://localhost:6379
APC_GRPC_PORT=50051
APC_LOG_LEVEL=INFO
```

### Docker Deployment

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY apc_core/ ./apc_core/
RUN cd apc_core && pip install -e .

COPY your_agent.py .
CMD ["python", "your_agent.py"]
```

```yaml
# docker-compose.yml
version: '3.8'
services:
  conductor:
    build: .
    environment:
      - APC_ROLE=conductor
      - APC_GRPC_PORT=50051
    ports:
      - "50051:50051"
  
  worker-1:
    build: .
    environment:
      - APC_ROLE=worker
      - APC_WORKER_ROLES=data-processor
      - APC_GRPC_PORT=50052
    ports:
      - "50052:50052"
  
  worker-2:
    build: .
    environment:
      - APC_ROLE=worker  
      - APC_WORKER_ROLES=ml-trainer
      - APC_GRPC_PORT=50053
    ports:
      - "50053:50053"
      
  redis:
    image: redis:alpine
    ports:
      - "6379:6379"
```

## 🎯 Testing Your Implementation

```python
"""
Test your APC implementation
"""
import pytest
import asyncio
from apc_core import Conductor, Worker

@pytest.mark.asyncio
async def test_basic_workflow():
    # Setup
    worker = Worker("test-worker")
    
    @worker.register_handler("test_task")
    async def test_task(params):
        return {"result": "success", "input": params}
    
    conductor = Conductor("test-conductor")
    
    # Test
    workflow = [{"step": "test_task", "params": {"test": "data"}}]
    result = await conductor.execute_workflow("test-batch", workflow)
    
    # Assert
    assert result["status"] == "completed"
    assert "test_task" in result["history"]

# Run tests
# pytest test_apc.py
```

## 📋 Best Practices

### 1. Error Handling

```python
class RobustWorker:
    def __init__(self):
        self.worker = Worker("robust-worker")
        
    @self.worker.register_handler("safe_task")
    async def safe_task(self, params):
        try:
            # Your logic here
            result = await self.process_data(params)
            return {"status": "success", "data": result}
        except ValueError as e:
            return {"status": "error", "error": "validation_error", "message": str(e)}
        except Exception as e:
            return {"status": "error", "error": "processing_error", "message": str(e)}
```

### 2. Monitoring and Observability

```python
import structlog
from apc_core import Conductor

class MonitoredConductor(Conductor):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = structlog.get_logger()
        
    async def execute_workflow(self, batch_id, workflow):
        self.logger.info("workflow_started", batch_id=batch_id, steps=len(workflow))
        
        try:
            result = await super().execute_workflow(batch_id, workflow)
            self.logger.info("workflow_completed", batch_id=batch_id, result=result)
            return result
        except Exception as e:
            self.logger.error("workflow_failed", batch_id=batch_id, error=str(e))
            raise
```

### 3. Load Balancing

```python
class LoadBalancedConductor:
    def __init__(self):
        self.worker_pools = {
            "data-processor": ["worker-1:50051", "worker-2:50052"],
            "ml-trainer": ["ml-1:50053", "ml-2:50054"]
        }
        
    async def select_worker(self, required_role):
        # Implement your load balancing logic
        available_workers = self.worker_pools.get(required_role, [])
        return self.get_least_loaded_worker(available_workers)
```

## 🚀 Ready to Deploy!

Your APC protocol is now production-ready. Here's how to get started:

1. **Start with examples**: Run `python test_working_example.py`
2. **Create your agents**: Use the patterns above
3. **Test thoroughly**: Implement proper error handling
4. **Deploy incrementally**: Start with simple workflows
5. **Monitor and scale**: Add observability and load balancing

## 📚 Additional Resources

- **[Complete Setup Guide](SETUP_GUIDE.md)** - Detailed installation instructions
- **[API Documentation](apc_core/)** - Full API reference
- **[Protocol Specification](apc-proto/apc.proto)** - Message formats
- **[Example Agents](examples/agents/)** - Real-world implementations

---

**The APC Protocol is ready for production use! 🎉**
