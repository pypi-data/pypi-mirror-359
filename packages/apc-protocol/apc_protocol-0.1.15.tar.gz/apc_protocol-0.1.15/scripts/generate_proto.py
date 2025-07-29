#!/usr/bin/env python
"""
Script to automate Protobuf code generation for APC protocol.
Usage:
    python generate_proto.py
"""
import subprocess
import sys
import os

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
proto_dir = os.path.join(project_root, 'proto')
out_dir = os.path.join(project_root, 'src', 'apc', 'messages')
proto_file = os.path.join(proto_dir, 'apc.proto')

cmd = [
    sys.executable, '-m', 'grpc_tools.protoc',
    f'-I={proto_dir}',
    f'--python_out={out_dir}',
    f'--grpc_python_out={out_dir}',
    proto_file
]

try:
    subprocess.check_call(cmd)
    print(f"\n[APC] Protobuf code generated successfully in {out_dir}!")
except subprocess.CalledProcessError as e:
    print("[APC] Protobuf code generation failed:", e)
    sys.exit(1)
