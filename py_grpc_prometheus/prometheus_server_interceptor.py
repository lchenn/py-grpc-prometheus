"""Interceptor a client call with prometheus"""

from timeit import default_timer

import grpc

from py_grpc_prometheus.server_metrics import GRPC_SERVER_HANDLED_LATENCY_SECONDS
from py_grpc_prometheus.server_metrics import GRPC_SERVER_STARTED_TOTAL


class PromServerInterceptor(grpc.ServerInterceptor):

  def intercept_service(self, continuation, handler_call_details):
    # e.g. /package.ServiceName/MethodName
    client_call_method = handler_call_details.method
    parts = client_call_method.split("/")
    grpc_service = parts[1]
    grpc_method = parts[2]

    GRPC_SERVER_STARTED_TOTAL.labels(
        grpc_type='UNARY',
        grpc_service=grpc_service,
        grpc_method=grpc_method).inc()

    start = default_timer()

    response = continuation(handler_call_details)
    print(response.unary_unary)
    GRPC_SERVER_HANDLED_LATENCY_SECONDS.labels(
        grpc_type='UNARY',
        grpc_service=grpc_service,
        grpc_method=grpc_method).observe(max(default_timer() - start, 0))
    # GRPC_SERVER_HANDLED_TOTAL.labels(
    #         grpc_type='UNARY',
    #         grpc_service=parts[1],
    #         grpc_method=parts[2],
    #         code=response.code().name).inc()
    return response
