"""
Basic gRPC example for APC protocol.
Demonstrates simple conductor-worker communication.
"""
import asyncio
import time
from apc import Conductor, Worker
from apc.transport import GRPCTransport

async def main():
    print("🚀 APC gRPC Basic Example")
    print("=" * 40)
    
    # Create worker
    worker = Worker("data-worker", roles=["data-processor"])
    worker_transport = GRPCTransport(port=50052)
    worker.bind_transport(worker_transport)
    
    # Register a simple data processing handler
    @worker.register_handler("process_data")
    async def process_data(params):
        print(f"💼 Processing data with params: {params}")
        await asyncio.sleep(1)  # Simulate work
        return {"processed_items": params.get("items", 0) * 2}
    
    # Start worker server
    await worker.start()
    await worker_transport.start_server()
    
    # Give server time to start
    await asyncio.sleep(1)
    
    # Create conductor
    conductor = Conductor("main-conductor")
    conductor_transport = GRPCTransport()
    conductor.bind_transport(conductor_transport)
    
    # Create a simple workflow
    workflow = conductor.create_workflow("data-processing")
    workflow.add_step("process_data", required_role="data-processor", 
                     params={"items": 10, "format": "json"})
    
    try:
        print("📋 Starting workflow execution...")
        result = await conductor.execute_workflow(workflow)
        print(f"✅ Workflow completed: {result}")
        
    except Exception as e:
        print(f"❌ Workflow failed: {e}")
    
    finally:
        await worker_transport.stop_server()
        await worker.stop()

if __name__ == "__main__":
    asyncio.run(main())
