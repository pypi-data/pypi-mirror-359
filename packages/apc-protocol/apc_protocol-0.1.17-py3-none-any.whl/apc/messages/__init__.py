"""Protocol buffer messages for APC."""

from . import apc_pb2, apc_pb2_grpc

# Message classes
BaseMessage = apc_pb2.BaseMessage
ProposeTaskRequest = apc_pb2.ProposeTaskRequest
AcceptResponse = apc_pb2.AcceptResponse
RejectResponse = apc_pb2.RejectResponse
CompletedNotification = apc_pb2.CompletedNotification
FailedNotification = apc_pb2.FailedNotification
TakeOverRequest = apc_pb2.TakeOverRequest
Response = apc_pb2.Response

# Service classes
APCServiceStub = apc_pb2_grpc.APCServiceStub
APCServiceServicer = apc_pb2_grpc.APCServiceServicer
add_APCServiceServicer_to_server = apc_pb2_grpc.add_APCServiceServicer_to_server

__all__ = [
    "BaseMessage",
    "ProposeTaskRequest", 
    "AcceptResponse",
    "RejectResponse",
    "CompletedNotification",
    "FailedNotification",
    "TakeOverRequest",
    "Response",
    "APCServiceStub",
    "APCServiceServicer",
    "add_APCServiceServicer_to_server",
]
