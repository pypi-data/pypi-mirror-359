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

# Automatically configure enhanced logging when APC is imported
from .helpers.logging import setup_apc_logging, get_logger
setup_apc_logging()  # Users get beautiful logs automatically!
"""

# Setup beautiful logging before importing other modules
from .helpers.logging import setup_apc_logging
setup_apc_logging()

from .core.conductor import Conductor
from .core.worker import Worker
from .core.checkpoint import CheckpointManager, InMemoryBackend, FileBackend, RedisBackend, S3Backend
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

# Enhanced LLM integration with streaming and colors
try:
    from .helpers.llms import AzureOpenAIStreamingClient, BaseLLMClient
    _has_llm = True
except ImportError:
    _has_llm = False

# Enhanced logging with streaming support
from .helpers.logging import (
    get_logger, 
    stream_llm_response, 
    log_llm_start, 
    log_llm_complete,
    ColorizedFormatter
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
    "FileBackend",
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
    
    # Enhanced logging and LLM integration
    "get_logger",
    "stream_llm_response",
    "log_llm_start", 
    "log_llm_complete",
    "ColorizedFormatter",
]

# Add LLM classes if available
if _has_llm:
    __all__.extend([
        "AzureOpenAIStreamingClient",
        "BaseLLMClient",
    ])
