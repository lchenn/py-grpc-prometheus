"""Interceptor a client call with prometheus"""

from timeit import default_timer

import grpc

from py_grpc_prometheus.client_metrics import GRPC_CLIENT_COMPLETED_COUNTER
from py_grpc_prometheus.client_metrics import GRPC_CLIENT_COMPLETED_LATENCY_SECONDS_HISTOGRAM
from py_grpc_prometheus.client_metrics import GRPC_CLIENT_STARTED_TOTAL_COUNTER


class PromClientInterceptor(grpc.UnaryUnaryClientInterceptor):

  def intercept_unary_unary(self, continuation, client_call_details, request):
    # e.g. /package.ServiceName/MethodName.
    client_call_method = client_call_details.method
    parts = client_call_method.split("/")
    grpc_service = parts[1]
    grpc_method = parts[2]

    GRPC_CLIENT_STARTED_TOTAL_COUNTER.labels(
        grpc_type='UNARY',
        grpc_service=grpc_service,
        grpc_method=grpc_method).inc()

    start = default_timer()
    response = continuation(client_call_details, request)
    GRPC_CLIENT_COMPLETED_LATENCY_SECONDS_HISTOGRAM.labels(
        grpc_type='UNARY',
        grpc_service=grpc_service,
        grpc_method=grpc_method).observe(max(default_timer() - start, 0))
    GRPC_CLIENT_COMPLETED_COUNTER.labels(
        grpc_type='UNARY',
        grpc_service=grpc_service,
        grpc_method=grpc_method,
        code=response.code().name).inc()
    return response
