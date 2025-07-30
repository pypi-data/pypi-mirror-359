#!/usr/bin/env python3
"""
APC Package Setup Script
Simple one-command setup for the APC protocol package.
"""
import subprocess
import sys
import os

def run_command(command, description):
    """Run a command and handle errors."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed!")
        print(f"Error: {e.stderr}")
        return False

def main():
    """Main setup function."""
    print("🚀 APC Package Setup")
    print("=" * 40)
    
    # Check if we're in the right directory
    if not os.path.exists("pyproject.toml"):
        print("❌ Please run this script from the APC package root directory")
        return False
    
    success = True
    
    # Install package
    if not run_command("pip install -e .", "Installing APC package"):
        success = False
    
    # Generate protobuf files
    if not run_command("python scripts/generate_proto.py", "Generating protobuf files"):
        success = False
    
    # Test package
    if success:
        if not run_command("python scripts/test_package.py", "Testing package"):
            success = False
    
    print("\n" + "=" * 40)
    if success:
        print("🎉 APC package setup completed successfully!")
        print("\n📚 Next steps:")
        print("• Run: python scripts/demo.py (for a complete demo)")
        print("• Check examples/basic/ for working examples")
        print("• Read docs/USAGE_GUIDE.md for tutorials")
    else:
        print("❌ Setup failed. Please check the errors above.")
    
    return success

if __name__ == "__main__":
    main()
