from prometheus_client import Counter
from prometheus_client import Histogram

GRPC_CLIENT_STARTED_TOTAL_COUNTER = Counter(
    "grpc_client_started_total",
    "Total number of RPCs started on the client",
    ["grpc_type", "grpc_service", "grpc_method"])

GRPC_CLIENT_COMPLETED_COUNTER = Counter(
    "grpc_client_completed",
    "Total number of RPCs completed on the client, "
    "regardless of success or failure.",
    ["grpc_type", "grpc_service", "grpc_method", "code"])

GRPC_CLIENT_COMPLETED_LATENCY_SECONDS_HISTOGRAM = Histogram(
    "grpc_client_completed_latency_seconds",
    "Histogram of rpc response latency (in seconds) for completed rpcs.",
    ["grpc_type", "grpc_service", "grpc_method"])


GRPC_CLIENT_MSG_RECEIVED_TOTAL_COUNTER = Counter(
    "grpc_client_msg_received_total",
    "Total number of stream messages received from the server.",
    ["grpc_type", "grpc_service", "grpc_method"])


GRPC_CLIENT_MSG_SENT_TOTAL_COUNTER = Counter(
    "grpc_client_msg_sent_total",
    "Total number of stream messages sent by the client.",
    ["grpc_type", "grpc_service", "grpc_method"]
)
