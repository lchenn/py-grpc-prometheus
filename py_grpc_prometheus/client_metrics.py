from prometheus_client import Counter
from prometheus_client import Histogram

GRPC_CLIENT_STARTED_COUNTER = Counter(
    "grpc_client_started_total",
    "Total number of RPCs started on the client",
    ["grpc_type", "grpc_service", "grpc_method"])

GRPC_CLIENT_HANDLED_COUNTER = Counter(
    "grpc_client_handled_total",
    "Total number of RPCs completed on the client, "
    "regardless of success or failure.",
    ["grpc_type", "grpc_service", "grpc_method", "grpc_code"])

GRPC_CLIENT_STREAM_MSG_RECEIVED = Counter(
    "grpc_client_msg_received_total",
    "Total number of RPC stream messages received by the client.",
    ["grpc_type", "grpc_service", "grpc_method"])

GRPC_CLIENT_STREAM_MSG_SENT = Counter(
    "grpc_client_msg_sent_total",
    "Total number of gRPC stream messages sent by the client.",
    ["grpc_type", "grpc_service", "grpc_method"]
)

GRPC_CLIENT_HANDLED_HISTOGRAM = Histogram(
    "grpc_client_handling_seconds",
    "Histogram of response latency (seconds) of the gRPC until it is finished by the application.",
    ["grpc_type", "grpc_service", "grpc_method"])

GRPC_CLIENT_STREAM_RECV_HISTOGRAM = Histogram(
    "grpc_client_msg_recv_handling_seconds",
    "Histogram of response latency (seconds) of the gRPC single message receive.",
    ["grpc_type", "grpc_service", "grpc_method"])

GRPC_CLIENT_STREAM_SEND_HISTOGRAM = Histogram(
    "grpc_client_msg_send_handling_seconds",
    "Histogram of response latency (seconds) of the gRPC single message send.",
    ["grpc_type", "grpc_service", "grpc_method"])

# Legacy metrics for backwards compatibility

LEGACY_GRPC_CLIENT_COMPLETED_COUNTER = Counter(
    "grpc_client_completed",
    "Total number of RPCs completed on the client, "
    "regardless of success or failure.",
    ["grpc_type", "grpc_service", "grpc_method", "code"])

LEGACY_GRPC_CLIENT_COMPLETED_LATENCY_SECONDS_HISTOGRAM = Histogram(
    "grpc_client_completed_latency_seconds",
    "Histogram of rpc response latency (in seconds) for completed rpcs.",
    ["grpc_type", "grpc_service", "grpc_method"])
