"""
Conductor implementation for APC protocol.
Orchestrates workflows and manages task distribution across workers.
Includes automatic failover and health monitoring capabilities.
"""
import asyncio
import time
import uuid
from enum import Enum, auto
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass

from .checkpoint import CheckpointManager
from .workflow import Workflow, WorkflowStep
from .health_monitor import ConductorHealthMonitor
from ..logging import get_logger, StructuredLogger

logger = get_logger(__name__)

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
    Includes automatic failover and health monitoring capabilities.
    
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
        checkpoint_manager: Optional[CheckpointManager] = None,
        enable_health_monitoring: bool = True,
        enable_auto_recovery: bool = True,
        priority: int = 100
    ):
        self.conductor_id = conductor_id
        # Use provided checkpoint manager or create default file-based one
        self.checkpoint_manager = checkpoint_manager or CheckpointManager(
            backend=None,  # Will use default FileBackend with "./checkpoints" 
            interval=30,   # More frequent checkpoints for production
            auto_recovery=enable_auto_recovery
        )
        self.enable_auto_recovery = enable_auto_recovery
        self.executions: Dict[str, WorkflowExecution] = {}
        self.available_workers: Set[str] = set()
        self.transport = None
        self._logger = StructuredLogger(logger) if not isinstance(logger, StructuredLogger) else logger
        
        # Health monitoring and failover
        self.health_monitor = None
        if enable_health_monitoring:
            self.health_monitor = ConductorHealthMonitor(
                conductor_id=conductor_id
            )
            self.health_monitor.on_takeover_required = self._handle_takeover_request
            
    async def start(self):
        """Start the conductor and health monitoring."""
        self._logger.info("Starting conductor", conductor_id=self.conductor_id)
        
        # Auto-recover workflows if enabled
        if self.enable_auto_recovery:
            await self._auto_recover_workflows()
        
        if self.health_monitor:
            await self.health_monitor.start()
            
    async def _auto_recover_workflows(self):
        """Automatically recover workflows from persistent checkpoints."""
        try:
            checkpoints = self.checkpoint_manager.discover_checkpoints()
            if checkpoints:
                self._logger.info(
                    "Discovered checkpoints for auto-recovery",
                    count=len(checkpoints),
                    conductor_id=self.conductor_id
                )
                
                for checkpoint_info in checkpoints:
                    batch_id = checkpoint_info["batch_id"]
                    try:
                        state = self.checkpoint_manager.load_checkpoint(batch_id)
                        if state and state.get("state") not in ["COMPLETED", "FAILED"]:
                            await self._resume_workflow_from_checkpoint(
                                state.get("workflow_id", f"recovered-{batch_id}"), 
                                state
                            )
                            self._logger.info(
                                "Auto-recovered workflow",
                                batch_id=batch_id,
                                workflow_id=state.get("workflow_id"),
                                conductor_id=self.conductor_id
                            )
                    except Exception as e:
                        self._logger.warning(
                            "Failed to auto-recover workflow",
                            batch_id=batch_id,
                            error=str(e),
                            conductor_id=self.conductor_id
                        )
            else:
                self._logger.info(
                    "No checkpoints found for auto-recovery",
                    conductor_id=self.conductor_id
                )
        except Exception as e:
            self._logger.error(
                "Auto-recovery process failed",
                error=str(e),
                conductor_id=self.conductor_id
            )
            
    async def stop(self):
        """Stop the conductor and health monitoring."""
        self._logger.info("Stopping conductor", conductor_id=self.conductor_id)
        
        # Stop all auto-checkpointing for running workflows
        for batch_id in list(self.executions.keys()):
            self.checkpoint_manager.stop_auto_checkpoint(batch_id)
        
        if self.health_monitor:
            await self.health_monitor.stop()
            
    async def _handle_takeover_request(self, failed_conductor_id: str, workflow_id: str):
        """Handle a request to take over a workflow from a failed conductor."""
        self._logger.warning(
            "Takeover request received",
            failed_conductor=failed_conductor_id,
            workflow_id=workflow_id
        )
        
        # Try to load the workflow state from checkpoint
        try:
            checkpoint = self.checkpoint_manager.load_checkpoint(workflow_id)
            if checkpoint:
                self._logger.info(
                    "Resuming workflow from checkpoint",
                    workflow_id=workflow_id,
                    failed_conductor=failed_conductor_id
                )
                await self._resume_workflow_from_checkpoint(workflow_id, checkpoint)
            else:
                self._logger.warning(
                    "No checkpoint found for workflow",
                    workflow_id=workflow_id
                )
        except Exception as e:
            self._logger.error(
                "Failed to resume workflow",
                workflow_id=workflow_id,
                error=str(e)
            )
            
    async def _resume_workflow_from_checkpoint(self, workflow_id: str, checkpoint: Dict[str, Any]):
        """Resume a workflow from a checkpoint after takeover."""
        try:
            # Deserialize the execution state
            execution = self._deserialize_execution_state(checkpoint)
            execution.workflow_id = workflow_id
            
            self.executions[execution.batch_id] = execution
            
            self._logger.info(
                "Workflow takeover successful, resuming execution",
                workflow_id=workflow_id,
                batch_id=execution.batch_id,
                current_step=execution.current_step
            )
            
            # Resume from the current step
            await self._execute_workflow_steps(execution, resume_from_step=execution.current_step)
            
        except Exception as e:
            self._logger.error(
                "Failed to resume workflow from checkpoint",
                workflow_id=workflow_id,
                error=str(e)
            )
            raise
        
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
        
        # Start automatic checkpointing for this workflow
        self.checkpoint_manager.start_auto_checkpoint(
            batch_id,
            lambda: self._serialize_execution_state(execution)
        )
        
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
            
            # Save final checkpoint and stop auto-checkpointing
            self.checkpoint_manager.save_checkpoint(
                batch_id,
                self._serialize_execution_state(execution),
                force=True
            )
            self.checkpoint_manager.stop_auto_checkpoint(batch_id)
            
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
            
            # Save failure checkpoint and stop auto-checkpointing
            self.checkpoint_manager.save_checkpoint(
                batch_id,
                self._serialize_execution_state(execution),
                force=True
            )
            self.checkpoint_manager.stop_auto_checkpoint(batch_id)
            
            self._logger.error(
                "Workflow execution failed",
                workflow_id=workflow_id,
                batch_id=batch_id,
                error=str(e)
            )
            raise
    
    def _serialize_execution_state(self, execution: WorkflowExecution) -> Dict[str, Any]:
        """Serialize execution state for checkpointing."""
        return {
            "workflow_id": execution.workflow_id,
            "batch_id": execution.batch_id,
            "current_step": execution.current_step,
            "state": execution.state.name,
            "history": execution.history,
            "started_at": execution.started_at,
            "completed_at": execution.completed_at,
            "workflow_data": {
                "name": execution.workflow.name,
                "steps": [
                    {
                        "name": step.name,
                        "required_role": step.required_role,
                        "dependencies": step.dependencies,
                        "params": step.params,
                        "timeout": step.timeout
                    }
                    for step in execution.workflow.steps
                ]
            }
        }
    
    def _deserialize_execution_state(self, checkpoint: Dict[str, Any]) -> WorkflowExecution:
        """Deserialize execution state from checkpoint."""
        workflow_data = checkpoint["workflow_data"]
        
        # Reconstruct the workflow
        workflow = Workflow(workflow_data["name"])
        for step_data in workflow_data["steps"]:
            workflow.add_step(
                name=step_data["name"],
                required_role=step_data["required_role"],
                dependencies=step_data.get("dependencies", []),
                params=step_data.get("params"),
                timeout=step_data.get("timeout", 60)
            )
        
        # Create execution object
        execution = WorkflowExecution(
            workflow_id=checkpoint["workflow_id"],
            batch_id=checkpoint["batch_id"],
            workflow=workflow,
            current_step=checkpoint["current_step"],
            state=ConductorState[checkpoint["state"]],
            history=checkpoint["history"],
            started_at=checkpoint["started_at"],
            completed_at=checkpoint["completed_at"]
        )
        
        return execution
    
    async def _execute_workflow_steps(self, execution: WorkflowExecution, resume_from_step: int = 0) -> None:
        """Execute all steps in a workflow, optionally resuming from a specific step."""
        execution.state = ConductorState.EXECUTING
        
        # Update health monitor with our current workload
        if self.health_monitor:
            active_workflows = {ex.workflow_id for ex in self.executions.values()}
            load_score = len(active_workflows) / 10.0  # Simple load calculation
            self.health_monitor.update_conductor_load(
                self.conductor_id, 
                load_score, 
                active_workflows
            )
        
        for step_index, step in enumerate(execution.workflow.steps[resume_from_step:], start=resume_from_step):
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
                conductor_id=self.conductor_id,
                step_name=step.name,
                step_index=step_index
            )
            
            try:
                await self._execute_step(execution, step)
                
                # Record step completion
                execution.history.append({
                    "step_name": step.name,
                    "step_index": step_index,
                    "completed_at": time.time(),
                    "status": "completed",
                    "conductor_id": self.conductor_id  # Track which conductor executed this step
                })
                
            except Exception as e:
                self._logger.error(
                    "Step execution failed",
                    batch_id=execution.batch_id,
                    step_name=step.name,
                    error=str(e)
                )
                
                # Request takeover if health monitoring is enabled
                if self.health_monitor:
                    await self.health_monitor.request_takeover(self.conductor_id, execution.workflow_id)
                
                raise
    
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

    def get_workflow_status(self, batch_id: str) -> Optional[Dict[str, Any]]:
        """Get the current status of a workflow execution."""
        execution = self.executions.get(batch_id)
        if execution:
            return {
                "workflow_id": execution.workflow_id,
                "batch_id": execution.batch_id,
                "state": execution.state.name,
                "current_step": execution.current_step,
                "total_steps": len(execution.workflow.steps),
                "started_at": execution.started_at,
                "completed_at": execution.completed_at,
                "history": execution.history
            }
        return None

    def list_active_workflows(self) -> List[Dict[str, Any]]:
        """List all currently active workflow executions."""
        return [
            self.get_workflow_status(batch_id) 
            for batch_id in self.executions.keys()
        ]

    def cleanup_completed_workflows(self) -> int:
        """Remove completed workflow executions from memory."""
        completed_batch_ids = [
            batch_id for batch_id, execution in self.executions.items()
            if execution.state in [ConductorState.COMPLETED, ConductorState.FAILED]
        ]
        
        for batch_id in completed_batch_ids:
            del self.executions[batch_id]
            self.checkpoint_manager.stop_auto_checkpoint(batch_id)
        
        return len(completed_batch_ids)

    def get_checkpoint_info(self, batch_id: str) -> Optional[Dict[str, Any]]:
        """Get checkpoint information for a workflow."""
        return self.checkpoint_manager.get_checkpoint_info(batch_id)

    def list_available_checkpoints(self) -> List[Dict[str, Any]]:
        """List all available checkpoints."""
        return self.checkpoint_manager.discover_checkpoints()

    @staticmethod
    def create_file_checkpoint_manager(checkpoint_dir: str = "./checkpoints", interval: int = 30) -> CheckpointManager:
        """Create a file-based checkpoint manager."""
        from .checkpoint import FileBackend
        return CheckpointManager(
            backend=FileBackend(checkpoint_dir),
            interval=interval,
            auto_recovery=True
        )

    @staticmethod
    def create_redis_checkpoint_manager(redis_client, interval: int = 30) -> CheckpointManager:
        """Create a Redis-based checkpoint manager."""
        from .checkpoint import RedisBackend
        return CheckpointManager(
            backend=RedisBackend(redis_client),
            interval=interval,
            auto_recovery=True
        )
