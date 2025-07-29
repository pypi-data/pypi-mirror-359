"""
Conductor implementation for APC protocol.
Orchestrates workflows and manages task distribution across workers.
"""
import asyncio
import time
import uuid
from enum import Enum, auto
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass
import structlog

from .checkpoint import CheckpointManager
from .workflow import Workflow, WorkflowStep

logger = structlog.get_logger()

class ConductorState(Enum):
    """States for conductor state machine."""
    IDLE = auto()
    PLANNING = auto()
    EXECUTING = auto()
    COMPLETED = auto()
    FAILED = auto()

@dataclass
class WorkflowExecution:
    """Represents a workflow execution instance."""
    workflow_id: str
    batch_id: str
    workflow: Workflow
    current_step: int = 0
    state: ConductorState = ConductorState.IDLE
    history: List[Dict[str, Any]] = None
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    
    def __post_init__(self):
        if self.history is None:
            self.history = []

class Conductor:
    """
    Conductor orchestrates workflows by proposing tasks to workers.
    
    Example:
        >>> conductor = Conductor("conductor-1")
        >>> workflow = conductor.create_workflow("data-pipeline")
        >>> workflow.add_step("extract", required_role="data-extractor")
        >>> workflow.add_step("transform", required_role="data-transformer") 
        >>> result = await conductor.execute_workflow(workflow)
    """
    
    def __init__(
        self, 
        conductor_id: str,
        checkpoint_manager: Optional[CheckpointManager] = None
    ):
        self.conductor_id = conductor_id
        self.checkpoint_manager = checkpoint_manager or CheckpointManager()
        self.executions: Dict[str, WorkflowExecution] = {}
        self.available_workers: Set[str] = set()
        self.transport = None
        self._logger = logger.bind(conductor_id=conductor_id)
        
    def bind_transport(self, transport) -> None:
        """Bind a transport layer for communication."""
        self.transport = transport
        self.transport.set_conductor(self)
        
    def create_workflow(self, name: str) -> Workflow:
        """Create a new workflow."""
        return Workflow(name)
    
    async def execute_workflow(self, workflow: Workflow, batch_id: Optional[str] = None) -> Dict[str, Any]:
        """Execute a workflow and return results."""
        if batch_id is None:
            batch_id = f"batch-{uuid.uuid4().hex[:8]}"
            
        workflow_id = f"workflow-{uuid.uuid4().hex[:8]}"
        
        execution = WorkflowExecution(
            workflow_id=workflow_id,
            batch_id=batch_id,
            workflow=workflow,
            started_at=time.time()
        )
        
        self.executions[batch_id] = execution
        
        self._logger.info(
            "Starting workflow execution",
            workflow_id=workflow_id,
            batch_id=batch_id,
            steps=len(workflow.steps)
        )
        
        try:
            execution.state = ConductorState.PLANNING
            await self._execute_workflow_steps(execution)
            execution.state = ConductorState.COMPLETED
            execution.completed_at = time.time()
            
            self._logger.info(
                "Workflow completed successfully",
                workflow_id=workflow_id,
                batch_id=batch_id,
                duration=execution.completed_at - execution.started_at
            )
            
            return {
                "status": "completed",
                "workflow_id": workflow_id,
                "batch_id": batch_id,
                "history": execution.history,
                "duration": execution.completed_at - execution.started_at
            }
            
        except Exception as e:
            execution.state = ConductorState.FAILED
            self._logger.error(
                "Workflow execution failed",
                workflow_id=workflow_id,
                batch_id=batch_id,
                error=str(e)
            )
            raise
    
    async def _execute_workflow_steps(self, execution: WorkflowExecution) -> None:
        """Execute all steps in a workflow."""
        execution.state = ConductorState.EXECUTING
        
        for step_index, step in enumerate(execution.workflow.steps):
            execution.current_step = step_index
            
            # Save checkpoint before executing step
            self.checkpoint_manager.save_checkpoint(
                execution.batch_id,
                self._serialize_execution_state(execution),
                force=True
            )
            
            self._logger.info(
                "Executing workflow step",
                batch_id=execution.batch_id,
                step_name=step.name,
                step_index=step_index
            )
            
            await self._execute_step(execution, step)
            
            # Record step completion
            execution.history.append({
                "step_name": step.name,
                "step_index": step_index,
                "completed_at": time.time(),
                "status": "completed"
            })
    
    async def _execute_step(self, execution: WorkflowExecution, step: WorkflowStep) -> None:
        """Execute a single workflow step."""
        if not self.transport:
            raise RuntimeError("No transport bound to conductor")
            
        # For now, propose the task and wait for completion
        # In a real implementation, this would be more sophisticated
        await self.transport.propose_task(
            batch_id=execution.batch_id,
            step_name=step.name,
            params=step.params or {},
            required_role=step.required_role
        )
    
    def on_accept(self, batch_id: str, step_name: str, worker_id: str) -> None:
        """Handle task acceptance from a worker."""
        execution = self.executions.get(batch_id)
        if execution:
            self._logger.info(
                "Task accepted by worker",
                batch_id=batch_id,
                step_name=step_name,
                worker_id=worker_id
            )
    
    def on_completed(self, batch_id: str, step_name: str, result: Dict[str, Any]) -> None:
        """Handle task completion from a worker."""
        execution = self.executions.get(batch_id)
        if execution:
            self._logger.info(
                "Task completed by worker",
                batch_id=batch_id,
                step_name=step_name,
                result=result
            )
    
    def on_failed(self, batch_id: str, step_name: str, error_code: str, error_msg: str) -> None:
        """Handle task failure from a worker."""
        execution = self.executions.get(batch_id)
        if execution:
            execution.state = ConductorState.FAILED
            self._logger.error(
                "Task failed",
                batch_id=batch_id,
                step_name=step_name,
                error_code=error_code,
                error_msg=error_msg
            )
    
    def on_worker_available(self, worker_id: str, capabilities: List[str]) -> None:
        """Handle worker availability notification."""
        self.available_workers.add(worker_id)
        self._logger.info(
            "Worker available",
            worker_id=worker_id,
            capabilities=capabilities
        )
    
    def on_worker_unavailable(self, worker_id: str) -> None:
        """Handle worker unavailability notification."""
        self.available_workers.discard(worker_id)
        self._logger.info("Worker unavailable", worker_id=worker_id)
    
    def _serialize_execution_state(self, execution: WorkflowExecution) -> Dict[str, Any]:
        """Serialize execution state for checkpointing."""
        return {
            "workflow_id": execution.workflow_id,
            "batch_id": execution.batch_id,
            "current_step": execution.current_step,
            "state": execution.state.name,
            "history": execution.history,
            "started_at": execution.started_at,
            "workflow_name": execution.workflow.name,
            "steps": [
                {
                    "name": step.name,
                    "required_role": step.required_role,
                    "params": step.params
                }
                for step in execution.workflow.steps
            ]
        }
    
    def recover_from_checkpoint(self, batch_id: str) -> bool:
        """Recover execution state from checkpoint."""
        state = self.checkpoint_manager.load_checkpoint(batch_id)
        if state:
            # Reconstruct workflow
            workflow = Workflow(state["workflow_name"])
            for step_data in state["steps"]:
                workflow.add_step(
                    step_data["name"],
                    required_role=step_data.get("required_role"),
                    params=step_data.get("params")
                )
            
            # Reconstruct execution
            execution = WorkflowExecution(
                workflow_id=state["workflow_id"],
                batch_id=state["batch_id"],
                workflow=workflow,
                current_step=state["current_step"],
                state=ConductorState[state["state"]],
                history=state["history"],
                started_at=state["started_at"]
            )
            
            self.executions[batch_id] = execution
            
            self._logger.info(
                "Recovered execution from checkpoint",
                batch_id=batch_id,
                workflow_id=execution.workflow_id,
                current_step=execution.current_step
            )
            return True
        
        return False
