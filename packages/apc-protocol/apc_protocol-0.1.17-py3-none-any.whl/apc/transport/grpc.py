"""
gRPC transport implementation for APC protocol.
"""
import asyncio
import grpc
import grpc.aio
from concurrent import futures
from typing import Dict, Any, Optional, List
import time

from ..messages import apc_pb2, apc_pb2_grpc

class GRPCWorkerServicer(apc_pb2_grpc.APCServiceServicer):
    """gRPC servicer for worker endpoints."""
    
    def __init__(self, transport):
        self.transport = transport
    
    async def ProposeTask(self, request, context):
        """Handle task proposal from conductor."""
        try:
            accepted = await self.transport.worker.on_propose_task(
                batch_id=request.base.batch_id,
                step_name=request.step_name,
                params=dict(request.params),
                required_role=request.role if request.role else None
            )
            
            base = apc_pb2.BaseMessage(
                batch_id=request.base.batch_id,
                sender_id=self.transport.worker.worker_id,
                timestamp=int(time.time())
            )
            
            return apc_pb2.Response(
                base=base,
                success=accepted,
                message="Accepted" if accepted else "Rejected"
            )
        except Exception as e:
            print(f"Error in ProposeTask: {e}")
            base = apc_pb2.BaseMessage(
                batch_id=request.base.batch_id,
                sender_id=self.transport.worker.worker_id,
                timestamp=int(time.time())
            )
            return apc_pb2.Response(
                base=base,
                success=False,
                message=f"Error: {str(e)}"
            )

class GRPCTransport:
    """gRPC transport layer for APC protocol."""
    
    def __init__(self, host: str = "localhost", port: int = 50051):
        self.host = host
        self.port = port
        self.server = None
        self.conductor = None
        self.worker = None
    
    def set_conductor(self, conductor):
        """Bind a conductor to this transport."""
        self.conductor = conductor
    
    def set_worker(self, worker):
        """Bind a worker to this transport."""
        self.worker = worker
    
    async def start_server(self):
        """Start the gRPC server (for workers)."""
        if not self.worker:
            raise RuntimeError("No worker bound to transport")
        
        self.server = grpc.aio.server()
        apc_pb2_grpc.add_APCServiceServicer_to_server(
            GRPCWorkerServicer(self), 
            self.server
        )
        
        listen_addr = f'{self.host}:{self.port}'
        self.server.add_insecure_port(listen_addr)
        
        await self.server.start()
        print(f"gRPC server started on {listen_addr}")
    
    async def stop_server(self):
        """Stop the gRPC server."""
        if self.server:
            await self.server.stop(0)
    
    async def propose_task(
        self,
        batch_id: str,
        step_name: str,
        params: Dict[str, Any],
        required_role: Optional[str] = None,
        worker_address: str = "localhost:50052"
    ):
        """Propose a task to a worker."""
        async with grpc.aio.insecure_channel(worker_address) as channel:
            stub = apc_pb2_grpc.APCServiceStub(channel)
            
            base = apc_pb2.BaseMessage(
                batch_id=batch_id,
                sender_id=self.conductor.conductor_id if self.conductor else "unknown",
                timestamp=int(time.time())
            )
            
            # Convert params dict to protobuf map
            request = apc_pb2.ProposeTaskRequest(
                base=base,
                step_name=step_name,
                role=required_role or ""
            )
            
            # Add params to the request
            for key, value in params.items():
                request.params[key] = str(value)
            
            try:
                response = await stub.ProposeTask(request)
                return response.success
            except grpc.RpcError as e:
                print(f"gRPC error proposing task: {e}")
                return False
    
    async def send_accept(self, batch_id: str, step_name: str, conductor_address: str = "localhost:50051"):
        """Send task acceptance (called by worker)."""
        async with grpc.aio.insecure_channel(conductor_address) as channel:
            stub = apc_pb2_grpc.APCServiceStub(channel)
            base = apc_pb2.BaseMessage(
                batch_id=batch_id,
                sender_id=self.worker.worker_id if self.worker else "unknown",
                timestamp=int(time.time())
            )
            request = apc_pb2.AcceptResponse(
                base=base,
                step_name=step_name
            )
            try:
                response = await stub.SendAccept(request)
                return response.success
            except grpc.RpcError as e:
                print(f"gRPC error sending accept: {e}")
                return False

    async def send_reject(self, batch_id: str, step_name: str, reason: str, conductor_address: str = "localhost:50051"):
        """Send task rejection (called by worker)."""
        async with grpc.aio.insecure_channel(conductor_address) as channel:
            stub = apc_pb2_grpc.APCServiceStub(channel)
            base = apc_pb2.BaseMessage(
                batch_id=batch_id,
                sender_id=self.worker.worker_id if self.worker else "unknown",
                timestamp=int(time.time())
            )
            request = apc_pb2.RejectResponse(
                base=base,
                step_name=step_name,
                reason=reason
            )
            try:
                response = await stub.SendReject(request)
                return response.success
            except grpc.RpcError as e:
                print(f"gRPC error sending reject: {e}")
                return False

    async def send_completed(
        self, 
        batch_id: str, 
        step_name: str, 
        success: bool, 
        result: Dict[str, Any],
        conductor_address: str = "localhost:50051"
    ):
        """Send task completion (called by worker)."""
        async with grpc.aio.insecure_channel(conductor_address) as channel:
            stub = apc_pb2_grpc.APCServiceStub(channel)
            base = apc_pb2.BaseMessage(
                batch_id=batch_id,
                sender_id=self.worker.worker_id if self.worker else "unknown",
                timestamp=int(time.time())
            )
            request = apc_pb2.CompletedNotification(
                base=base,
                step_name=step_name,
                success=success
            )
            for key, value in result.items():
                request.result[key] = str(value)
            try:
                response = await stub.SendCompleted(request)
                return response.success
            except grpc.RpcError as e:
                print(f"gRPC error sending completed: {e}")
                return False

    async def send_failed(
        self, 
        batch_id: str, 
        step_name: str, 
        error_code: str, 
        error_msg: str,
        conductor_address: str = "localhost:50051"
    ):
        """Send task failure (called by worker)."""
        async with grpc.aio.insecure_channel(conductor_address) as channel:
            stub = apc_pb2_grpc.APCServiceStub(channel)
            base = apc_pb2.BaseMessage(
                batch_id=batch_id,
                sender_id=self.worker.worker_id if self.worker else "unknown",
                timestamp=int(time.time())
            )
            request = apc_pb2.FailedNotification(
                base=base,
                step_name=step_name,
                error_code=error_code,
                error_msg=error_msg
            )
            try:
                response = await stub.SendFailed(request)
                return response.success
            except grpc.RpcError as e:
                print(f"gRPC error sending failed: {e}")
                return False

    async def announce_availability(self, worker_id: str, roles: List[str], conductor_address: str = "localhost:50051"):
        """Announce worker availability."""
        # This method should notify the conductor of worker availability.
        # For now, we call a method on the conductor directly if available, otherwise this should be a gRPC call.
        if self.conductor:
            self.conductor.on_worker_available(worker_id, roles)
        else:
            # If conductor is remote, implement a gRPC call for worker registration (not defined in proto yet)
            print(f"Announce availability: worker {worker_id} with roles {roles}")
        return True
