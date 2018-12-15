"""Interceptor a client call with prometheus"""

from timeit import default_timer

import grpc

import py_grpc_prometheus.grpc_method as grpc_method
from py_grpc_prometheus.client_metrics import GRPC_CLIENT_COMPLETED_COUNTER
from py_grpc_prometheus.client_metrics import GRPC_CLIENT_COMPLETED_LATENCY_SECONDS_HISTOGRAM
from py_grpc_prometheus.client_metrics import GRPC_CLIENT_MSG_RECEIVED_TOTAL_COUNTER
from py_grpc_prometheus.client_metrics import GRPC_CLIENT_MSG_SENT_TOTAL_COUNTER
from py_grpc_prometheus.client_metrics import GRPC_CLIENT_STARTED_TOTAL_COUNTER


class PromClientInterceptor(grpc.UnaryUnaryClientInterceptor,
                            grpc.UnaryStreamClientInterceptor,
                            grpc.StreamUnaryClientInterceptor,
                            grpc.StreamStreamClientInterceptor):
  """
  Intercept gRPC client requests.
  """

  def intercept_unary_unary(self, continuation, client_call_details, request):
    start = default_timer()
    handler = continuation(client_call_details, request)

    grpc_service_name, grpc_method_name, _ = grpc_method.GrpcMethod.split_method_call(
        client_call_details)
    grpc_type = grpc_method.UNARY

    GRPC_CLIENT_STARTED_TOTAL_COUNTER.labels(
        grpc_type=grpc_type,
        grpc_service=grpc_service_name,
        grpc_method=grpc_method_name).inc()

    GRPC_CLIENT_COMPLETED_LATENCY_SECONDS_HISTOGRAM.labels(
        grpc_type=grpc_type,
        grpc_service=grpc_service_name,
        grpc_method=grpc_method_name).observe(max(default_timer() - start, 0))
    GRPC_CLIENT_COMPLETED_COUNTER.labels(
        grpc_type=grpc_type,
        grpc_service=grpc_service_name,
        grpc_method=grpc_method_name,
        code=handler.code().name).inc()
    return handler

  def intercept_unary_stream(self, continuation, client_call_details, request):
    start = default_timer()
    handler = continuation(client_call_details, request)

    grpc_service_name, grpc_method_name, _ = grpc_method.GrpcMethod.split_method_call(
        client_call_details)
    grpc_type = grpc_method.SERVER_STREAMING

    GRPC_CLIENT_STARTED_TOTAL_COUNTER.labels(
        grpc_type=grpc_type,
        grpc_service=grpc_service_name,
        grpc_method=grpc_method_name).inc()
    GRPC_CLIENT_COMPLETED_LATENCY_SECONDS_HISTOGRAM.labels(
        grpc_type=grpc_type,
        grpc_service=grpc_service_name,
        grpc_method=grpc_method_name).observe(max(default_timer() - start, 0))
    return self.wrap_iterator(handler,
                              GRPC_CLIENT_MSG_RECEIVED_TOTAL_COUNTER,
                              grpc_type,
                              grpc_service_name,
                              grpc_method_name)

  def intercept_stream_unary(self, continuation, client_call_details, request_iterator):
    grpc_service_name, grpc_method_name, _ = grpc_method.GrpcMethod.split_method_call(
        client_call_details)
    grpc_type = grpc_method.CLIENT_STREAMING

    request_iterator = self.wrap_iterator(request_iterator,
                                          GRPC_CLIENT_MSG_SENT_TOTAL_COUNTER,
                                          grpc_type,
                                          grpc_service_name,
                                          grpc_method_name)
    start = default_timer()
    handler = continuation(client_call_details, request_iterator)
    GRPC_CLIENT_STARTED_TOTAL_COUNTER.labels(
        grpc_type=grpc_type,
        grpc_service=grpc_service_name,
        grpc_method=grpc_method_name).inc()
    GRPC_CLIENT_COMPLETED_LATENCY_SECONDS_HISTOGRAM.labels(
        grpc_type=grpc_type,
        grpc_service=grpc_service_name,
        grpc_method=grpc_method_name).observe(max(default_timer() - start, 0))
    return handler

  def intercept_stream_stream(self, continuation, client_call_details, request_iterator):
    grpc_service_name, grpc_method_name, _ = grpc_method.GrpcMethod.split_method_call(
        client_call_details)
    grpc_type = grpc_method.BIDI_STREAMING
    response_iterator = continuation(
        client_call_details,
        self.wrap_iterator(request_iterator, GRPC_CLIENT_MSG_SENT_TOTAL_COUNTER,
                           grpc_type, grpc_service_name, grpc_method_name))
    return self.wrap_iterator(response_iterator, GRPC_CLIENT_MSG_RECEIVED_TOTAL_COUNTER,
                              grpc_type, grpc_service_name, grpc_method_name)

  def wrap_iterator(self, iterator, counter, grpc_type, grpc_service_name,
                    grpc_method_name):
    for item in iterator:
      counter.labels(
          grpc_type=grpc_type,
          grpc_service=grpc_service_name,
          grpc_method=grpc_method_name).inc()
      yield item
