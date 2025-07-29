"""
APC (Agent Protocol Conductor)

A protocol for decentralized, resilient, and auditable orchestration 
of heterogeneous AI agent ecosystems.

Basic Usage:
    >>> from apc import Conductor, Worker
    >>> from apc.transport import GRPCTransport
    
    >>> # Create a conductor
    >>> conductor = Conductor("conductor-1")
    >>> transport = GRPCTransport(port=50051)
    >>> conductor.bind_transport(transport)
    
    >>> # Define a workflow
    >>> workflow = conductor.create_workflow("data-pipeline")
    >>> workflow.add_step("extract", required_role="data-extractor")
    >>> workflow.add_step("transform", required_role="data-transformer") 
    >>> workflow.add_step("load", required_role="data-loader")
    
    >>> # Start the workflow
    >>> result = await conductor.execute_workflow(workflow)
"""

from .core.conductor import Conductor
from .core.worker import Worker
from .core.checkpoint import CheckpointManager, InMemoryBackend, RedisBackend, S3Backend
from .core.workflow import Workflow, WorkflowStep
from .transport.grpc import GRPCTransport
from .transport.websocket import WebSocketTransport
from .messages import (
    BaseMessage,
    ProposeTaskRequest,
    AcceptResponse,
    RejectResponse,
    CompletedNotification,
    FailedNotification,
    TakeOverRequest,
    Response,
)

__version__ = "0.2.0"
__author__ = "APC Contributors"

__all__ = [
    # Core classes
    "Conductor",
    "Worker", 
    "Workflow",
    "WorkflowStep",
    
    # Transport
    "GRPCTransport",
    "WebSocketTransport",
    
    # Checkpoint management
    "CheckpointManager",
    "InMemoryBackend", 
    "RedisBackend",
    "S3Backend",
    
    # Messages
    "BaseMessage",
    "ProposeTaskRequest",
    "AcceptResponse", 
    "RejectResponse",
    "CompletedNotification",
    "FailedNotification",
    "TakeOverRequest",
    "Response",
]
