"""
Worker implementation for APC protocol.
Executes tasks proposed by conductors.
"""
import asyncio
import time
from enum import Enum, auto
from typing import Dict, List, Optional, Any, Callable, Set
from dataclasses import dataclass
import logging

from .checkpoint import CheckpointManager

logger = logging.getLogger(__name__)

class WorkerState(Enum):
    """States for worker state machine."""
    IDLE = auto()
    EXECUTING = auto()
    COMPLETED = auto()
    FAILED = auto()

@dataclass
class TaskExecution:
    """Represents a task execution instance."""
    task_id: str
    batch_id: str
    step_name: str
    params: Dict[str, Any]
    state: WorkerState = WorkerState.IDLE
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class Worker:
    """
    Worker executes tasks proposed by conductors.
    
    Example:
        >>> worker = Worker("worker-1", roles=["data-processor"])
        >>> 
        >>> @worker.register_handler("process_data")
        >>> async def process_data(params):
        ...     # Process the data
        ...     return {"processed_items": 100}
        >>> 
        >>> await worker.start()
    """
    
    def __init__(
        self,
        worker_id: str,
        roles: Optional[List[str]] = None,
        checkpoint_manager: Optional[CheckpointManager] = None
    ):
        self.worker_id = worker_id
        self.roles = set(roles or [])
        self.checkpoint_manager = checkpoint_manager or CheckpointManager()
        self.handlers: Dict[str, Callable] = {}
        self.executions: Dict[str, TaskExecution] = {}
        self.transport = None
        self._running = False
        
    def bind_transport(self, transport) -> None:
        """Bind a transport layer for communication."""
        self.transport = transport
        self.transport.set_worker(self)
    
    def register_handler(self, step_name: str, handler: Optional[Callable] = None):
        """
        Register a handler for a specific step type.
        Can be used as a decorator or regular function.
        """
        def decorator(func: Callable):
            self.handlers[step_name] = func
            return func
        
        if handler is not None:
            self.handlers[step_name] = handler
            return handler
        
        return decorator
    
    def add_role(self, role: str) -> None:
        """Add a role capability to this worker."""
        self.roles.add(role)
    
    def remove_role(self, role: str) -> None:
        """Remove a role capability from this worker."""
        self.roles.discard(role)
    
    def can_handle(self, step_name: str, required_role: Optional[str] = None) -> bool:
        """Check if this worker can handle a specific task."""
        # Check if we have a handler for this step
        if step_name not in self.handlers:
            return False
        
        # Check if we have the required role
        if required_role and required_role not in self.roles:
            return False
        
        return True
    
    async def start(self) -> None:
        """Start the worker."""
        self._running = True
        logger.info(f"Worker {self.worker_id} started with roles: {list(self.roles)}")
        
        # Notify transport that we're available
        if self.transport:
            await self.transport.announce_availability(self.worker_id, list(self.roles))
    
    async def stop(self) -> None:
        """Stop the worker."""
        self._running = False
        logger.info(f"Worker {self.worker_id} stopped")
    
    async def on_propose_task(
        self,
        batch_id: str,
        step_name: str,
        params: Dict[str, Any],
        required_role: Optional[str] = None
    ) -> bool:
        """Handle task proposal from conductor."""
        logger.info(
            f"Worker {self.worker_id} received task proposal: {step_name} "
            f"(batch: {batch_id}, role: {required_role})"
        )
        
        if not self.can_handle(step_name, required_role):
            logger.info(f"Worker {self.worker_id} cannot handle task {step_name}")
            if self.transport:
                await self.transport.send_reject(
                    batch_id=batch_id,
                    step_name=step_name,
                    reason=f"Cannot handle step '{step_name}' or role '{required_role}'"
                )
            return False
        
        # Accept the task
        task_id = f"{batch_id}-{step_name}-{int(time.time())}"
        execution = TaskExecution(
            task_id=task_id,
            batch_id=batch_id,
            step_name=step_name,
            params=params,
            started_at=time.time()
        )
        
        self.executions[task_id] = execution
        
        # Send acceptance
        if self.transport:
            await self.transport.send_accept(
                batch_id=batch_id,
                step_name=step_name
            )
        
        # Execute the task
        asyncio.create_task(self._execute_task(execution))
        return True
    
    async def _execute_task(self, execution: TaskExecution) -> None:
        """Execute a task."""
        try:
            execution.state = WorkerState.EXECUTING
            
            # Save checkpoint
            self.checkpoint_manager.save_checkpoint(
                execution.batch_id,
                self._serialize_execution_state(execution),
                force=True
            )
            
            logger.info(f"Executing task {execution.step_name} for batch {execution.batch_id}")
            
            # Get the handler
            handler = self.handlers[execution.step_name]
            
            # Execute the handler
            if asyncio.iscoroutinefunction(handler):
                result = await handler(execution.params)
            else:
                result = handler(execution.params)
            
            # Task completed successfully
            execution.state = WorkerState.COMPLETED
            execution.completed_at = time.time()
            execution.result = result
            
            logger.info(
                f"Task {execution.step_name} completed successfully "
                f"(duration: {execution.completed_at - execution.started_at:.2f}s)"
            )
            
            # Send completion notification
            if self.transport:
                await self.transport.send_completed(
                    batch_id=execution.batch_id,
                    step_name=execution.step_name,
                    success=True,
                    result=result or {}
                )
            
        except Exception as e:
            # Task failed
            execution.state = WorkerState.FAILED
            execution.error = str(e)
            
            logger.error(f"Task {execution.step_name} failed: {e}")
            
            # Send failure notification
            if self.transport:
                await self.transport.send_failed(
                    batch_id=execution.batch_id,
                    step_name=execution.step_name,
                    error_code="EXECUTION_ERROR",
                    error_msg=str(e)
                )
        
        finally:
            # Save final checkpoint
            self.checkpoint_manager.save_checkpoint(
                execution.batch_id,
                self._serialize_execution_state(execution),
                force=True
            )
    
    def _serialize_execution_state(self, execution: TaskExecution) -> Dict[str, Any]:
        """Serialize execution state for checkpointing."""
        return {
            "task_id": execution.task_id,
            "batch_id": execution.batch_id,
            "step_name": execution.step_name,
            "params": execution.params,
            "state": execution.state.name,
            "started_at": execution.started_at,
            "completed_at": execution.completed_at,
            "result": execution.result,
            "error": execution.error,
            "worker_id": self.worker_id,
            "roles": list(self.roles)
        }
    
    def recover_from_checkpoint(self, batch_id: str) -> bool:
        """Recover execution state from checkpoint."""
        state = self.checkpoint_manager.load_checkpoint(batch_id)
        if state:
            execution = TaskExecution(
                task_id=state["task_id"],
                batch_id=state["batch_id"],
                step_name=state["step_name"],
                params=state["params"],
                state=WorkerState[state["state"]],
                started_at=state["started_at"],
                completed_at=state.get("completed_at"),
                result=state.get("result"),
                error=state.get("error")
            )
            
            self.executions[execution.task_id] = execution
            
            logger.info(
                f"Recovered task execution from checkpoint: {execution.task_id} "
                f"(state: {execution.state.name})"
            )
            return True
        
        return False
