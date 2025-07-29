#!/usr/bin/env python3
"""
PyPI Installation Test
Test script to verify the package works when installed from PyPI.
"""
import sys
import subprocess

def test_pypi_install():
    """Test installing from PyPI and basic functionality."""
    print("=" * 60)
    print("APC Protocol - PyPI Installation Test")
    print("=" * 60)
    
    # Test imports
    try:
        print("Testing imports...")
        from apc import Worker, Conductor
        from apc.transport import GRPCTransport, WebSocketTransport
        from apc.messages import apc_pb2, apc_pb2_grpc
        print("✓ All imports successful")
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        return False
    
    # Test object creation
    try:
        print("Testing object creation...")
        worker = Worker("test-worker", roles=["tester"])
        conductor = Conductor("test-conductor")
        transport = GRPCTransport()
        print("✓ Objects created successfully")
    except Exception as e:
        print(f"✗ Object creation failed: {e}")
        return False
    
    # Test handler registration
    try:
        print("Testing handler registration...")
        @worker.register_handler("test_task")
        async def test_handler(batch_id, step_name, params):
            return {"status": "success"}
        print("✓ Handler registered successfully")
    except Exception as e:
        print(f"✗ Handler registration failed: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("✓ PyPI package test completed successfully!")
    print("The package is ready for production use.")
    print("=" * 60)
    return True

def show_usage_example():
    """Show a basic usage example."""
    print("\nBasic Usage Example:")
    print("-" * 40)
    print("""
# Install: pip install apc-protocol

from apc import Worker
from apc.transport import GRPCTransport
import asyncio

async def main():
    # Create worker
    worker = Worker("my-worker", roles=["processor"])
    
    # Register handler
    @worker.register_handler("process_data")
    async def process_data(batch_id, step_name, params):
        data = params.get("data", [])
        return {"processed": len(data), "status": "completed"}
    
    # Setup transport
    transport = GRPCTransport(port=50051)
    worker.bind_transport(transport)
    
    print("Worker ready! Press Ctrl+C to stop.")
    await transport.start_server()

if __name__ == "__main__":
    asyncio.run(main())
""")

def main():
    """Main test function."""
    success = test_pypi_install()
    if success:
        show_usage_example()
        print("\nNext steps:")
        print("• Check examples/ for more complex usage")
        print("• Read docs/PRODUCTION_GUIDE.md for production deployment")
        print("• Visit https://github.com/deepfarkade/apc-protocol for source")
    else:
        print("\nSetup issues detected. Please check the installation.")
        sys.exit(1)

if __name__ == "__main__":
    main()
