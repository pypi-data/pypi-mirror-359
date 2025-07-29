#!/usr/bin/env python3
"""
Simple APC Test - Quick test to verify the package works
"""
import sys
import os

def test_basic_imports():
    """Test that all core components can be imported."""
    print("Testing APC Package Imports...")
    
    try:
        # Test core imports
        from apc import Conductor, Worker
        print("X Core components imported successfully")
        
        # Test transport imports  
        from apc.transport import GRPCTransport, WebSocketTransport
        print("X Transport layers imported successfully")
        
        # Test message imports
        from apc.messages import apc_pb2, apc_pb2_grpc
        print("X Protocol messages imported successfully")
        
        return True
        
    except ImportError as e:
        print(f"X Import error: {e}")
        print("Make sure to run: python scripts/generate_proto.py")
        print("Make sure to run: pip install -e .")
        return False

def test_basic_creation():
    """Test that basic objects can be created."""
    print("\nTesting Object Creation...")
    
    try:
        from apc import Conductor, Worker
        from apc.transport import GRPCTransport
        
        # Create conductor
        conductor = Conductor("test-conductor")
        print(f"+ Conductor created: {conductor.conductor_id}")
        
        # Create worker
        worker = Worker("test-worker", roles=["tester"])
        print(f"+ Worker created: {worker.worker_id}")
        
        # Create transport
        transport = GRPCTransport()
        print(f"+ Transport created: gRPC on {transport.host}:{transport.port}")
        
        return True
        
    except Exception as e:
        print(f"- Creation error: {e}")
        return False

def test_handler_registration():
    """Test that handlers can be registered."""
    print("\nTesting Handler Registration...")
    
    try:
        from apc import Worker
        
        worker = Worker("handler-test-worker", roles=["handler-tester"])
        
        # Register a simple handler
        @worker.register_handler("test_task")
        def test_handler(batch_id: str, step_name: str, params: dict):
            return {"status": "test_completed", "input": params}
        
        print("+ Handler registered successfully")
        
        # Check if handler is registered
        if "test_task" in worker.handlers:
            print("+ Handler found in worker registry")
        else:
            print("- Handler not found in registry")
            return False
            
        return True
        
    except Exception as e:
        print(f"- Handler registration error: {e}")
        return False

def show_package_structure():
    """Show the package structure."""
    print("\nAPC Package Structure:")
    print("src/apc/")
    print("├── __init__.py")
    print("├── core/")
    print("│   ├── conductor.py")
    print("│   ├── worker.py")
    print("│   ├── workflow.py")
    print("│   └── checkpoint.py")
    print("├── transport/")
    print("│   ├── grpc.py")
    print("│   └── websocket.py")
    print("└── messages/")
    print("    ├── apc_pb2.py")
    print("    └── apc_pb2_grpc.py")

def show_usage_examples():
    """Show simple usage examples."""
    print("\nSimple Usage Examples:")
    print()
    print("1. Create a Worker:")
    print("   from apc import Worker")
    print("   worker = Worker('my-worker', roles=['processor'])")
    print()
    print("2. Register a Handler:")
    print("   @worker.register_handler('my_task')")
    print("   async def handle_task(batch_id, step_name, params):")
    print("       return {'result': 'completed'}")
    print()
    print("3. Create a Conductor:")
    print("   from apc import Conductor")
    print("   conductor = Conductor('my-conductor')")
    print()
    print("4. Set up Transport:")
    print("   from apc.transport import GRPCTransport")
    print("   transport = GRPCTransport(port=50051)")
    print("   worker.bind_transport(transport)")

def main():
    """Main test function."""
    print("APC Package Test Suite")
    print("=" * 50)
    
    all_passed = True
    
    # Test imports
    if not test_basic_imports():
        all_passed = False
        print("\nSetup needed:")
        print("1. Run: python scripts/generate_proto.py")
        print("2. Run: pip install -e .")
        print("3. Run this test again")
        return
    
    # Test object creation
    if not test_basic_creation():
        all_passed = False
    
    # Test handler registration
    if not test_handler_registration():
        all_passed = False
    
    # Show structure and examples
    show_package_structure()
    show_usage_examples()
    
    print("\n" + "=" * 50)
    if all_passed:
        print("All tests passed! APC package is working correctly.")
        print()
        print("Next steps:")
        print("• Run: python scripts/demo.py (for a complete demo)")
        print("• Check examples/basic/ for working examples")
        print("• Read docs/USAGE_GUIDE.md for tutorials")
    else:
        print("Some tests failed. Please check the setup.")

if __name__ == "__main__":
    main()
