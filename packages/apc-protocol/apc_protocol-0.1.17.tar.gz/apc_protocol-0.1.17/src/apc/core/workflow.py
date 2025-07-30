"""
Workflow and WorkflowStep classes for APC protocol.
Defines the structure and execution flow of multi-step processes.
"""
from dataclasses import dataclass
from typing import Dict, List, Optional, Any

@dataclass
class WorkflowStep:
    """Represents a single step in a workflow."""
    name: str
    required_role: Optional[str] = None
    params: Optional[Dict[str, Any]] = None
    dependencies: Optional[List[str]] = None
    timeout: Optional[int] = None
    retry_count: int = 0
    
    def __post_init__(self):
        if self.params is None:
            self.params = {}
        if self.dependencies is None:
            self.dependencies = []

class Workflow:
    """
    Represents a workflow consisting of multiple steps.
    
    Example:
        >>> workflow = Workflow("data-pipeline")
        >>> workflow.add_step("extract", required_role="data-extractor")
        >>> workflow.add_step("transform", required_role="data-transformer", 
        ...                   dependencies=["extract"])
        >>> workflow.add_step("load", required_role="data-loader", 
        ...                   dependencies=["transform"])
    """
    
    def __init__(self, name: str, description: Optional[str] = None):
        self.name = name
        self.description = description
        self.steps: List[WorkflowStep] = []
        self._step_names: set = set()
    
    def add_step(
        self,
        name: str,
        required_role: Optional[str] = None,
        params: Optional[Dict[str, Any]] = None,
        dependencies: Optional[List[str]] = None,
        timeout: Optional[int] = None,
        retry_count: int = 0
    ) -> WorkflowStep:
        """Add a step to the workflow."""
        if name in self._step_names:
            raise ValueError(f"Step '{name}' already exists in workflow")
        
        step = WorkflowStep(
            name=name,
            required_role=required_role,
            params=params or {},
            dependencies=dependencies or [],
            timeout=timeout,
            retry_count=retry_count
        )
        
        # Validate dependencies
        for dep in step.dependencies:
            if dep not in self._step_names:
                raise ValueError(f"Dependency '{dep}' not found in workflow")
        
        self.steps.append(step)
        self._step_names.add(name)
        return step
    
    def get_step(self, name: str) -> Optional[WorkflowStep]:
        """Get a step by name."""
        for step in self.steps:
            if step.name == name:
                return step
        return None
    
    def get_executable_steps(self, completed_steps: List[str]) -> List[WorkflowStep]:
        """Get steps that can be executed given completed steps."""
        executable = []
        completed_set = set(completed_steps)
        
        for step in self.steps:
            if step.name not in completed_set:
                # Check if all dependencies are satisfied
                if all(dep in completed_set for dep in step.dependencies):
                    executable.append(step)
        
        return executable
    
    def validate(self) -> bool:
        """Validate the workflow for cycles and dependency issues."""
        # Simple cycle detection using DFS
        visited = set()
        rec_stack = set()
        
        def has_cycle(step_name: str) -> bool:
            if step_name in rec_stack:
                return True
            if step_name in visited:
                return False
            
            visited.add(step_name)
            rec_stack.add(step_name)
            
            step = self.get_step(step_name)
            if step:
                for dep in step.dependencies:
                    if has_cycle(dep):
                        return True
            
            rec_stack.remove(step_name)
            return False
        
        # Check each step for cycles
        for step in self.steps:
            if step.name not in visited:
                if has_cycle(step.name):
                    raise ValueError(f"Cycle detected in workflow involving step '{step.name}'")
        
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert workflow to dictionary representation."""
        return {
            "name": self.name,
            "description": self.description,
            "steps": [
                {
                    "name": step.name,
                    "required_role": step.required_role,
                    "params": step.params,
                    "dependencies": step.dependencies,
                    "timeout": step.timeout,
                    "retry_count": step.retry_count
                }
                for step in self.steps
            ]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Workflow":
        """Create workflow from dictionary representation."""
        workflow = cls(data["name"], data.get("description"))
        
        for step_data in data["steps"]:
            workflow.add_step(
                name=step_data["name"],
                required_role=step_data.get("required_role"),
                params=step_data.get("params"),
                dependencies=step_data.get("dependencies"),
                timeout=step_data.get("timeout"),
                retry_count=step_data.get("retry_count", 0)
            )
        
        return workflow
