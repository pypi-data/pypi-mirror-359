# APC Production Usage Guide

## Installation & Setup

### PyPI Installation (Recommended)
```bash
pip install apc-protocol
```

### Verify Installation
```python
from apc import Worker, Conductor
from apc.transport import GRPCTransport, WebSocketTransport
print("APC installed successfully!")
```

## Core Concepts

### 1. Workers - Task Executors
Workers execute specific tasks and can have multiple roles.

```python
from apc import Worker

# Create a worker with specific roles
worker = Worker("data-processor", roles=["processor", "analyzer"])

# Register task handlers
@worker.register_handler("process_csv")
async def process_csv(batch_id: str, step_name: str, params: dict):
    file_path = params["file_path"]
    # Your processing logic
    return {"processed_rows": 1000, "status": "completed"}

@worker.register_handler("analyze_data")
async def analyze_data(batch_id: str, step_name: str, params: dict):
    data = params["data"]
    # Your analysis logic
    return {"insights": ["trend1", "trend2"], "confidence": 0.95}
```

### 2. Conductors - Workflow Orchestrators
Conductors manage multi-step workflows and coordinate workers.

```python
from apc import Conductor

conductor = Conductor("workflow-manager")

# Define workflow steps
async def run_data_pipeline(input_file: str):
    batch_id = f"pipeline-{int(time.time())}"
    
    # Step 1: Process CSV
    result1 = await conductor.propose_task(
        batch_id=batch_id,
        step_name="process_csv",
        params={"file_path": input_file},
        required_role="processor"
    )
    
    # Step 2: Analyze results
    result2 = await conductor.propose_task(
        batch_id=batch_id,
        step_name="analyze_data", 
        params={"data": result1["processed_rows"]},
        required_role="analyzer"
    )
    
    return result2
```

### 3. Transport Layers
Choose the appropriate transport for your use case.

#### gRPC (High Performance)
```python
from apc.transport import GRPCTransport

# For workers
worker_transport = GRPCTransport(port=50051)
worker.bind_transport(worker_transport)
await worker_transport.start_server()

# For conductors
conductor_transport = GRPCTransport(port=50052)
conductor.bind_transport(conductor_transport)
```

#### WebSocket (Web-Friendly)
```python
from apc.transport import WebSocketTransport

transport = WebSocketTransport(port=8080)
worker.bind_transport(transport)
await transport.start_server()
```

## Production Patterns

### 1. Microservice Architecture
```python
# service_a.py - Data Extraction Service
from apc import Worker
import asyncio

async def main():
    worker = Worker("data-extractor", roles=["extractor"])
    
    @worker.register_handler("extract_from_api")
    async def extract_api(batch_id, step_name, params):
        api_url = params["url"]
        # API extraction logic
        return {"data": "extracted_data", "count": 100}
    
    transport = GRPCTransport(port=50051)
    worker.bind_transport(transport)
    await transport.start_server()

if __name__ == "__main__":
    asyncio.run(main())
```

```python
# service_b.py - Data Processing Service  
from apc import Worker
import asyncio

async def main():
    worker = Worker("data-processor", roles=["processor"])
    
    @worker.register_handler("clean_data")
    async def clean_data(batch_id, step_name, params):
        raw_data = params["data"]
        # Data cleaning logic
        return {"cleaned_data": "processed", "errors": 0}
    
    transport = GRPCTransport(port=50052)
    worker.bind_transport(transport)
    await transport.start_server()

if __name__ == "__main__":
    asyncio.run(main())
```

```python
# orchestrator.py - Main Workflow Conductor
from apc import Conductor
import asyncio

async def main():
    conductor = Conductor("main-orchestrator")
    transport = GRPCTransport(port=50050)
    conductor.bind_transport(transport)
    
    # Run workflow
    batch_id = "prod-batch-001"
    
    # Step 1: Extract
    extract_result = await transport.propose_task(
        batch_id=batch_id,
        step_name="extract_from_api",
        params={"url": "https://api.example.com/data"},
        worker_address="localhost:50051"
    )
    
    # Step 2: Process  
    process_result = await transport.propose_task(
        batch_id=batch_id,
        step_name="clean_data",
        params={"data": extract_result},
        worker_address="localhost:50052"
    )
    
    print(f"Workflow completed: {process_result}")

if __name__ == "__main__":
    asyncio.run(main())
```

### 2. AI/LLM Integration
```python
from apc import Worker
import openai
import asyncio

worker = Worker("ai-worker", roles=["text-generator", "summarizer"])

@worker.register_handler("generate_content")
async def generate_content(batch_id: str, step_name: str, params: dict):
    prompt = params["prompt"]
    max_tokens = params.get("max_tokens", 100)
    
    response = await openai.ChatCompletion.acreate(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=max_tokens
    )
    
    return {
        "content": response.choices[0].message.content,
        "tokens_used": response.usage.total_tokens,
        "model": "gpt-4"
    }

@worker.register_handler("summarize_text")
async def summarize_text(batch_id: str, step_name: str, params: dict):
    text = params["text"]
    
    response = await openai.ChatCompletion.acreate(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Summarize the following text concisely."},
            {"role": "user", "content": text}
        ]
    )
    
    return {
        "summary": response.choices[0].message.content,
        "original_length": len(text),
        "summary_length": len(response.choices[0].message.content)
    }
```

### 3. Error Handling & Resilience
```python
from apc import Worker
import asyncio
import logging

logger = logging.getLogger(__name__)

worker = Worker("resilient-worker", roles=["processor"])

@worker.register_handler("fault_tolerant_task")
async def fault_tolerant_task(batch_id: str, step_name: str, params: dict):
    max_retries = params.get("max_retries", 3)
    retry_count = params.get("retry_count", 0)
    
    try:
        # Your potentially failing operation
        result = await some_external_api_call(params["data"])
        return {"result": result, "retries": retry_count}
        
    except Exception as e:
        logger.error(f"Task failed: {e}")
        
        if retry_count < max_retries:
            # Return failure with retry info
            raise Exception(f"Retry {retry_count + 1}/{max_retries}: {str(e)}")
        else:
            # Max retries exceeded
            return {
                "error": str(e),
                "retries": retry_count,
                "status": "failed_permanently"
            }
```

### 4. Distributed Checkpointing
```python
from apc import Conductor
from apc.core import RedisCheckpointManager

# Use Redis for distributed state management
checkpoint_manager = RedisCheckpointManager(
    host="redis-cluster.example.com",
    port=6379,
    db=0,
    password="your-redis-password"
)

conductor = Conductor("distributed-conductor")
conductor.set_checkpoint_manager(checkpoint_manager)

# Now your workflow state is automatically saved to Redis
# and can be recovered by any conductor instance
```

## Deployment Strategies

### Docker Deployment
```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["python", "your_agent.py"]
```

```yaml
# docker-compose.yml
version: '3.8'
services:
  conductor:
    build: .
    command: python orchestrator.py
    ports:
      - "50050:50050"
    
  data-extractor:
    build: .
    command: python service_a.py
    ports:
      - "50051:50051"
      
  data-processor:
    build: .
    command: python service_b.py
    ports:
      - "50052:50052"
      
  redis:
    image: redis:alpine
    ports:
      - "6379:6379"
```

### Kubernetes Deployment
```yaml
# k8s-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: apc-worker
spec:
  replicas: 3
  selector:
    matchLabels:
      app: apc-worker
  template:
    metadata:
      labels:
        app: apc-worker
    spec:
      containers:
      - name: worker
        image: your-registry/apc-worker:latest
        ports:
        - containerPort: 50051
        env:
        - name: WORKER_ROLE
          value: "data-processor"
        - name: REDIS_HOST
          value: "redis-service"
```

## Best Practices

1. **Use Specific Roles**: Define clear, specific roles for your workers
2. **Handle Errors Gracefully**: Always include error handling in your handlers
3. **Log Everything**: Use structured logging for debugging and monitoring
4. **Health Checks**: Implement health check endpoints for your services
5. **Resource Management**: Set appropriate timeouts and resource limits
6. **Security**: Use mTLS in production environments
7. **Monitoring**: Implement metrics and monitoring for your agents

## Next Steps

1. Start with simple examples from `examples/basic/`
2. Build your first worker and conductor
3. Add transport layers (gRPC or WebSocket)
4. Implement error handling and checkpointing
5. Scale to multiple workers and distributed deployment
6. Add monitoring and security as needed

For more examples, see the [examples/](../examples/) directory.
