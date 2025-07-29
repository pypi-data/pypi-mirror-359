#!/usr/bin/env python3
"""
APC Protocol Demo - Simple demonstration of all features
This script shows how easy it is to use the APC package.
"""
import asyncio
import time
from apc import Conductor, Worker
from apc.transport import GRPCTransport

async def demo_basic_workflow():
    """Demonstrate a basic workflow without getting stuck."""
    print("APC Protocol Demo")
    print("=" * 50)
    
    # Create a simple workflow
    print("1. Creating conductor and worker...")
    
    # Create conductor
    conductor = Conductor("demo-conductor")
    
    # Create worker
    worker = Worker("demo-worker", roles=["processor"])
    
    # Register a simple handler that doesn't require external dependencies
    @worker.register_handler("simple_task")
    async def handle_simple_task(batch_id: str, step_name: str, params: dict):
        print(f"   ✓ Worker processing: {step_name}")
        print(f"   Parameters: {params}")
        
        # Simulate some work
        await asyncio.sleep(0.5)
        
        result = {
            "status": "completed",
            "processed_items": params.get("items", 0),
            "message": "Task completed successfully!"
        }
        
        print(f"   Result: {result}")
        return result
    
    print("2. Setting up transport...")
    
    # Create transport for worker
    worker_transport = GRPCTransport(port=50052)
    worker.bind_transport(worker_transport)
    
    # Create transport for conductor  
    conductor_transport = GRPCTransport(port=50051)
    conductor.bind_transport(conductor_transport)
    
    print("3. Starting worker server...")
    
    # Start worker server
    await worker_transport.start_server()
    
    # Give server time to start
    await asyncio.sleep(0.5)
    
    print("4. Executing workflow...")
    
    # Define a simple workflow
    workflow_steps = [
        {
            "step_name": "simple_task",
            "role": "processor",
            "params": {"items": 10, "type": "demo"}
        }
    ]
    
    # Execute workflow
    batch_id = f"demo-batch-{int(time.time())}"
    
    for step in workflow_steps:
        print(f"   🔄 Executing step: {step['step_name']}")
        
        success = await conductor_transport.propose_task(
            batch_id=batch_id,
            step_name=step["step_name"],
            params=step["params"],
            required_role=step["role"],
            worker_address="localhost:50052"
        )
        
        if success:
            print(f"   ✅ Step {step['step_name']} completed successfully!")
        else:
            print(f"   ❌ Step {step['step_name']} failed!")
    
    print("5. Cleaning up...")
    
    # Stop server
    await worker_transport.stop_server()
    
    print("🎉 Demo completed!")
    print("\n" + "=" * 50)
    print("📚 What happened:")
    print("• Created a conductor to orchestrate tasks")
    print("• Created a worker with a simple task handler")
    print("• Set up gRPC communication between them")
    print("• Executed a workflow step successfully")
    print("• Cleaned up resources")
    print("\n💡 This demonstrates the core APC protocol features!")

async def demo_multiple_workers():
    """Demonstrate multiple workers with different roles."""
    print("\n🔧 Multiple Workers Demo")
    print("=" * 50)
    
    # Create workers with different roles
    data_worker = Worker("data-worker", roles=["data-processor"])
    text_worker = Worker("text-worker", roles=["text-processor"])
    
    # Register handlers
    @data_worker.register_handler("process_data")
    async def process_data(batch_id: str, step_name: str, params: dict):
        print(f"   📊 Data Worker: Processing {params.get('records', 0)} records")
        await asyncio.sleep(0.3)
        return {"processed_records": params.get('records', 0)}
    
    @text_worker.register_handler("process_text")
    async def process_text(batch_id: str, step_name: str, params: dict):
        print(f"   📝 Text Worker: Processing '{params.get('text', '')}'")
        await asyncio.sleep(0.3)
        return {"processed_text": params.get('text', '').upper()}
    
    print("• Multiple workers with specialized roles created")
    print("• Each worker can handle different types of tasks")
    print("• This enables building complex, distributed workflows")

async def demo_error_handling():
    """Demonstrate error handling capabilities."""
    print("\n🛡️ Error Handling Demo")
    print("=" * 50)
    
    worker = Worker("error-demo-worker", roles=["error-tester"])
    
    @worker.register_handler("failing_task")
    async def failing_task(batch_id: str, step_name: str, params: dict):
        if params.get("should_fail", False):
            raise Exception("Simulated task failure")
        return {"status": "success"}
    
    print("• Workers can handle errors gracefully")
    print("• Failed tasks can be retried or handed to other workers")
    print("• Checkpointing ensures no work is lost")

def print_package_info():
    """Print information about the APC package."""
    print("\n📦 APC Package Information")
    print("=" * 50)
    print("✅ Installation: pip install -e .")
    print("✅ Core Components:")
    print("   • Conductor: Orchestrates workflows")
    print("   • Worker: Executes tasks")
    print("   • Transport: gRPC/WebSocket communication")
    print("   • Checkpointing: State persistence")
    print("✅ Key Features:")
    print("   • Distributed agent coordination")
    print("   • Fault tolerance and recovery")
    print("   • Pluggable transport layers")
    print("   • Cross-language compatibility")
    print("✅ Example Usage:")
    print("   • Basic workflows: examples/basic/")
    print("   • Agent patterns: examples/agents/")
    print("   • Documentation: README.md, USAGE_GUIDE.md")

async def main():
    """Main demo function."""
    try:
        # Print package info
        print_package_info()
        
        # Run basic demo
        await demo_basic_workflow()
        
        # Show multiple workers concept
        await demo_multiple_workers()
        
        # Show error handling concept
        await demo_error_handling()
        
        print("\n🎯 Next Steps:")
        print("• Check out examples/basic/ for more examples")
        print("• Read USAGE_GUIDE.md for detailed tutorials")
        print("• Build your own agents with custom logic")
        print("• Integrate with your favorite AI models")
        
    except KeyboardInterrupt:
        print("\n👋 Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo error: {e}")
        print("💡 Make sure to run 'python generate_proto.py' first")

if __name__ == "__main__":
    asyncio.run(main())
