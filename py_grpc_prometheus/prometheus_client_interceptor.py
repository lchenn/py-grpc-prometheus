"""Interceptor a client call with prometheus"""

from timeit import default_timer

import grpc

from py_grpc_prometheus.client_metrics import GRPC_CLIENT_COMPLETED_COUNTER
from py_grpc_prometheus.client_metrics import GRPC_CLIENT_COMPLETED_LATENCY_SECONDS_HISTOGRAM
from py_grpc_prometheus.client_metrics import GRPC_CLIENT_STARTED_TOTAL_COUNTER
from py_grpc_prometheus.grpc_method import GrpcMethod


class PromClientInterceptor(grpc.UnaryUnaryClientInterceptor):

  def intercept_unary_unary(self, continuation, client_call_details, request):

    grpc_service_name, grpc_method_name, _ = GrpcMethod.split_method_call(client_call_details)

    GRPC_CLIENT_STARTED_TOTAL_COUNTER.labels(
        grpc_type='UNARY',
        grpc_service=grpc_service_name,
        grpc_method=grpc_method_name).inc()

    start = default_timer()
    handler = continuation(client_call_details, request)
    GRPC_CLIENT_COMPLETED_LATENCY_SECONDS_HISTOGRAM.labels(
        grpc_type='UNARY',
        grpc_service=grpc_service_name,
        grpc_method=grpc_method_name).observe(max(default_timer() - start, 0))
    GRPC_CLIENT_COMPLETED_COUNTER.labels(
        grpc_type='UNARY',
        grpc_service=grpc_service_name,
        grpc_method=grpc_method_name,
        code=handler.code().name).inc()
    return handler
