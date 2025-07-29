"""
WebSocket transport implementation for APC protocol.
"""
import asyncio
import json
import websockets
from typing import Dict, Any, Optional, List
import time

class WebSocketTransport:
    """WebSocket transport layer for APC protocol."""
    
    def __init__(self, host: str = "localhost", port: int = 8765):
        self.host = host
        self.port = port
        self.server = None
        self.conductor = None
        self.worker = None
        self.connections = set()
    
    def set_conductor(self, conductor):
        """Bind a conductor to this transport."""
        self.conductor = conductor
    
    def set_worker(self, worker):
        """Bind a worker to this transport."""
        self.worker = worker
    
    async def start_server(self):
        """Start the WebSocket server (for workers)."""
        if not self.worker:
            raise RuntimeError("No worker bound to transport")
        
        self.server = await websockets.serve(
            self._handle_connection, 
            self.host, 
            self.port
        )
        print(f"WebSocket server started on ws://{self.host}:{self.port}")
    
    async def stop_server(self):
        """Stop the WebSocket server."""
        if self.server:
            self.server.close()
            await self.server.wait_closed()
    
    async def _handle_connection(self, websocket, path=""):
        """Handle incoming WebSocket connections."""
        self.connections.add(websocket)
        try:
            async for message in websocket:
                await self._handle_message(websocket, message)
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            self.connections.discard(websocket)
    
    async def _handle_message(self, websocket, message):
        """Handle incoming WebSocket message."""
        try:
            data = json.loads(message)
            message_type = data.get('type')
            
            if message_type == 'ProposeTask':
                accepted = await self.worker.on_propose_task(
                    batch_id=data.get('batch_id'),
                    step_name=data.get('step_name'),
                    params=data.get('params', {}),
                    required_role=data.get('role')
                )
                
                response = {
                    'type': 'Response',
                    'batch_id': data.get('batch_id'),
                    'step_name': data.get('step_name'),
                    'sender_id': self.worker.worker_id,
                    'timestamp': int(time.time()),
                    'success': accepted,
                    'message': 'Accepted' if accepted else 'Rejected'
                }
                
                await websocket.send(json.dumps(response))
                
        except Exception as e:
            print(f"Error handling WebSocket message: {e}")
    
    async def propose_task(
        self,
        batch_id: str,
        step_name: str,
        params: Dict[str, Any],
        required_role: Optional[str] = None,
        worker_uri: str = "ws://localhost:8765"
    ):
        """Propose a task to a worker via WebSocket."""
        message = {
            'type': 'ProposeTask',
            'batch_id': batch_id,
            'sender_id': self.conductor.conductor_id if self.conductor else "unknown",
            'timestamp': int(time.time()),
            'step_name': step_name,
            'role': required_role,
            'params': params
        }
        
        try:
            async with websockets.connect(worker_uri) as websocket:
                await websocket.send(json.dumps(message))
                response = await websocket.recv()
                response_data = json.loads(response)
                return response_data.get('success', False)
        except Exception as e:
            print(f"WebSocket error proposing task: {e}")
            return False
    
    async def send_accept(self, batch_id: str, step_name: str):
        """Send task acceptance."""
        # Implementation depends on specific requirements
        pass
    
    async def send_reject(self, batch_id: str, step_name: str, reason: str):
        """Send task rejection."""
        # Implementation depends on specific requirements
        pass
    
    async def send_completed(
        self, 
        batch_id: str, 
        step_name: str, 
        success: bool, 
        result: Dict[str, Any]
    ):
        """Send task completion."""
        # Implementation depends on specific requirements
        pass
    
    async def send_failed(
        self, 
        batch_id: str, 
        step_name: str, 
        error_code: str, 
        error_msg: str
    ):
        """Send task failure."""
        # Implementation depends on specific requirements
        pass
    
    async def announce_availability(self, worker_id: str, roles: List[str]):
        """Announce worker availability."""
        # Implementation depends on specific requirements
        pass
