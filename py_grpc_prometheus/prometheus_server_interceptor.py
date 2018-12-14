"""Interceptor a client call with prometheus"""

from timeit import default_timer

import grpc

from py_grpc_prometheus.server_metrics import GRPC_SERVER_HANDLED_LATENCY_SECONDS
from py_grpc_prometheus.server_metrics import GRPC_SERVER_STARTED_TOTAL
from py_grpc_prometheus.grpc_method import GrpcMethod


class PromServerInterceptor(grpc.ServerInterceptor):

  # https://grpc.io/grpc/python/grpc.html#service-side-interceptor
  def intercept_service(self, continuation, handler_call_details):

    grpc_service_name, grpc_method_name, _ = GrpcMethod.split_method_call(handler_call_details)
    handler = continuation(handler_call_details)

    grpc_type = GrpcMethod.get_method_type(handler.request_streaming, handler.response_streaming)

    GRPC_SERVER_STARTED_TOTAL.labels(
        grpc_type=grpc_type,
        grpc_service=grpc_service_name,
        grpc_method=grpc_method_name).inc()

    start = default_timer()

    GRPC_SERVER_HANDLED_LATENCY_SECONDS.labels(
        grpc_type=grpc_type,
        grpc_service=grpc_service_name,
        grpc_method=grpc_method_name).observe(max(default_timer() - start, 0))
    # GRPC_SERVER_HANDLED_TOTAL.labels(
    #         grpc_type='UNARY',
    #         grpc_service=parts[1],
    #         grpc_method=parts[2],
    #         code=response.code().name).inc()
    return handler
