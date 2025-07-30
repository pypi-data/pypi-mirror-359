import asyncio
import json
import websockets
from apc.logging import get_logger

logger = get_logger("conductor_ws_server")

class ConductorWebSocketServer:
    def __init__(self, conductor, host="localhost", port=8766):
        self.conductor = conductor
        self.host = host
        self.port = port
        self.server = None
        self.connections = set()

    async def start(self):
        self.server = await websockets.serve(self._handle_connection, self.host, self.port)
        logger.warning(f"Conductor WebSocket server started on ws://{self.host}:{self.port}")

    async def stop(self):
        if self.server:
            self.server.close()
            await self.server.wait_closed()

    async def _handle_connection(self, websocket, path=""):
        self.connections.add(websocket)
        try:
            async for message in websocket:
                await self._handle_message(websocket, message)
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            self.connections.discard(websocket)

    async def _handle_message(self, websocket, message):
        try:
            data = json.loads(message)
            message_type = data.get('type')
            batch_id = data.get('batch_id')
            step_name = data.get('step_name')
            worker_id = data.get('sender_id') or data.get('worker_id')
            if message_type == 'Accept':
                self.conductor.on_accept(batch_id, step_name, worker_id)
                logger.warning(f"Received Accept from worker {worker_id} for {batch_id}:{step_name}")
                await websocket.send(json.dumps({'success': True}))
            elif message_type == 'Reject':
                reason = data.get('reason', '')
                self.conductor.on_failed(batch_id, step_name, 'REJECTED', reason)
                logger.error(f"Received Reject from worker {worker_id} for {batch_id}:{step_name} reason={reason}")
                await websocket.send(json.dumps({'success': True}))
            elif message_type == 'Completed':
                result = data.get('result', {})
                self.conductor.on_completed(batch_id, step_name, result)
                logger.warning(f"Received Completed from worker {worker_id} for {batch_id}:{step_name}")
                await websocket.send(json.dumps({'success': True}))
            elif message_type == 'Failed':
                error_code = data.get('error_code', '')
                error_msg = data.get('error_msg', '')
                self.conductor.on_failed(batch_id, step_name, error_code, error_msg)
                logger.error(f"Received Failed from worker {worker_id} for {batch_id}:{step_name} code={error_code} msg={error_msg}")
                await websocket.send(json.dumps({'success': True}))
            elif message_type == 'AnnounceAvailability':
                roles = data.get('roles', [])
                self.conductor.on_worker_available(worker_id, roles)
                logger.warning(f"Received AnnounceAvailability from worker {worker_id} roles={roles}")
                await websocket.send(json.dumps({'success': True}))
            else:
                logger.error(f"Unknown message type: {message_type}")
                await websocket.send(json.dumps({'success': False, 'error': 'Unknown message type'}))
        except Exception as e:
            logger.error(f"Error handling message: {e}")
            await websocket.send(json.dumps({'success': False, 'error': str(e)}))
