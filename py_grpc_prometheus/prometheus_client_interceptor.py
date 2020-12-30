"""Interceptor a client call with prometheus"""

from timeit import default_timer

import grpc

import py_grpc_prometheus.grpc_utils as grpc_utils
from py_grpc_prometheus.client_metrics import GRPC_CLIENT_HANDLED_COUNTER
from py_grpc_prometheus.client_metrics import GRPC_CLIENT_HANDLED_HISTOGRAM
from py_grpc_prometheus.client_metrics import GRPC_CLIENT_STARTED_COUNTER
from py_grpc_prometheus.client_metrics import GRPC_CLIENT_STREAM_MSG_RECEIVED
from py_grpc_prometheus.client_metrics import GRPC_CLIENT_STREAM_MSG_SENT
from py_grpc_prometheus.client_metrics import GRPC_CLIENT_STREAM_RECV_HISTOGRAM
from py_grpc_prometheus.client_metrics import GRPC_CLIENT_STREAM_SEND_HISTOGRAM
# Legacy metrics
from py_grpc_prometheus.client_metrics import LEGACY_GRPC_CLIENT_COMPLETED_COUNTER
from py_grpc_prometheus.client_metrics import LEGACY_GRPC_CLIENT_COMPLETED_LATENCY_SECONDS_HISTOGRAM


class PromClientInterceptor(grpc.UnaryUnaryClientInterceptor,
                            grpc.UnaryStreamClientInterceptor,
                            grpc.StreamUnaryClientInterceptor,
                            grpc.StreamStreamClientInterceptor):
  """
  Intercept gRPC client requests.
  """

  def __init__(
            self,
            enable_client_handling_time_histogram=False,
            enable_client_stream_receive_time_histogram=False,
            enable_client_stream_send_time_histogram=False,
            legacy=False
  ):
    self._enable_client_handling_time_histogram = enable_client_handling_time_histogram
    self._enable_client_stream_receive_time_histogram = enable_client_stream_receive_time_histogram
    self._enable_client_stream_send_time_histogram = enable_client_stream_send_time_histogram
    self._legacy = legacy

  def intercept_unary_unary(self, continuation, client_call_details, request):
    grpc_service_name, grpc_method_name, _ = grpc_utils.split_method_call(client_call_details)
    grpc_type = grpc_utils.UNARY


    GRPC_CLIENT_STARTED_COUNTER.labels(
        grpc_type=grpc_type,
        grpc_service=grpc_service_name,
        grpc_method=grpc_method_name).inc()

    start = default_timer()
    handler = continuation(client_call_details, request)
    if self._legacy:
      LEGACY_GRPC_CLIENT_COMPLETED_LATENCY_SECONDS_HISTOGRAM.labels(
          grpc_type=grpc_type,
          grpc_service=grpc_service_name,
          grpc_method=grpc_method_name).observe(max(default_timer() - start, 0))
    elif self._enable_client_handling_time_histogram:
      GRPC_CLIENT_HANDLED_HISTOGRAM.labels(
          grpc_type=grpc_type,
          grpc_service=grpc_service_name,
          grpc_method=grpc_method_name).observe(max(default_timer() - start, 0))

    if self._legacy:
      LEGACY_GRPC_CLIENT_COMPLETED_COUNTER.labels(
          grpc_type=grpc_type,
          grpc_service=grpc_service_name,
          grpc_method=grpc_method_name,
          code=handler.code().name).inc()
    else:
      GRPC_CLIENT_HANDLED_COUNTER.labels(
          grpc_type=grpc_type,
          grpc_service=grpc_service_name,
          grpc_method=grpc_method_name,
          grpc_code=handler.code().name).inc()

    return handler

  def intercept_unary_stream(self, continuation, client_call_details, request):
    grpc_service_name, grpc_method_name, _ = grpc_utils.split_method_call(client_call_details)
    grpc_type = grpc_utils.SERVER_STREAMING

    GRPC_CLIENT_STARTED_COUNTER.labels(
        grpc_type=grpc_type,
        grpc_service=grpc_service_name,
        grpc_method=grpc_method_name).inc()

    start = default_timer()
    handler = continuation(client_call_details, request)
    if self._legacy:
      LEGACY_GRPC_CLIENT_COMPLETED_LATENCY_SECONDS_HISTOGRAM.labels(
          grpc_type=grpc_type,
          grpc_service=grpc_service_name,
          grpc_method=grpc_method_name).observe(max(default_timer() - start, 0))

    elif self._enable_client_handling_time_histogram:
      GRPC_CLIENT_HANDLED_HISTOGRAM.labels(
          grpc_type=grpc_type,
          grpc_service=grpc_service_name,
          grpc_method=grpc_method_name).observe(max(default_timer() - start, 0))

    handler = grpc_utils.wrap_iterator_inc_counter(
        handler,
        GRPC_CLIENT_STREAM_MSG_RECEIVED,
        grpc_type,
        grpc_service_name,
        grpc_method_name)

    if self._enable_client_stream_receive_time_histogram and not self._legacy:
      GRPC_CLIENT_STREAM_RECV_HISTOGRAM.labels(
          grpc_type=grpc_type,
          grpc_service=grpc_service_name,
          grpc_method=grpc_method_name).observe(max(default_timer() - start, 0))

    return handler

  def intercept_stream_unary(self, continuation, client_call_details, request_iterator):
    grpc_service_name, grpc_method_name, _ = grpc_utils.split_method_call(client_call_details)
    grpc_type = grpc_utils.CLIENT_STREAMING

    iterator_metric = GRPC_CLIENT_STREAM_MSG_SENT

    request_iterator = grpc_utils.wrap_iterator_inc_counter(
        request_iterator,
        iterator_metric,
        grpc_type,
        grpc_service_name,
        grpc_method_name)

    start = default_timer()
    handler = continuation(client_call_details, request_iterator)

    if self._legacy:
      GRPC_CLIENT_STARTED_COUNTER.labels(
          grpc_type=grpc_type,
          grpc_service=grpc_service_name,
          grpc_method=grpc_method_name).inc()
      LEGACY_GRPC_CLIENT_COMPLETED_LATENCY_SECONDS_HISTOGRAM.labels(
          grpc_type=grpc_type,
          grpc_service=grpc_service_name,
          grpc_method=grpc_method_name).observe(max(default_timer() - start, 0))
    else:
      GRPC_CLIENT_STARTED_COUNTER.labels(
          grpc_type=grpc_type,
          grpc_service=grpc_service_name,
          grpc_method=grpc_method_name).inc()
      if self._enable_client_handling_time_histogram:
        GRPC_CLIENT_HANDLED_HISTOGRAM.labels(
            grpc_type=grpc_type,
            grpc_service=grpc_service_name,
            grpc_method=grpc_method_name).observe(max(default_timer() - start, 0))

    if self._enable_client_stream_send_time_histogram and not self._legacy:
      GRPC_CLIENT_STREAM_SEND_HISTOGRAM.labels(
          grpc_type=grpc_type,
          grpc_service=grpc_service_name,
          grpc_method=grpc_method_name).observe(max(default_timer() - start, 0))

    return handler

  def intercept_stream_stream(self, continuation, client_call_details, request_iterator):
    grpc_service_name, grpc_method_name, _ = grpc_utils.split_method_call(
        client_call_details)
    grpc_type = grpc_utils.BIDI_STREAMING
    start = default_timer()

    iterator_sent_metric = GRPC_CLIENT_STREAM_MSG_SENT

    response_iterator = continuation(
        client_call_details,
        grpc_utils.wrap_iterator_inc_counter(
            request_iterator,
            iterator_sent_metric,
            grpc_type,
            grpc_service_name,
            grpc_method_name))

    if self._enable_client_stream_send_time_histogram and not self._legacy:
      GRPC_CLIENT_STREAM_SEND_HISTOGRAM.labels(
          grpc_type=grpc_type,
          grpc_Service=grpc_service_name,
          grpc_method=grpc_method_name).observe(max(default_timer() - start, 0))

    iterator_received_metric = GRPC_CLIENT_STREAM_MSG_RECEIVED

    response_iterator = grpc_utils.wrap_iterator_inc_counter(
        response_iterator,
        iterator_received_metric,
        grpc_type,
        grpc_service_name,
        grpc_method_name)

    if self._enable_client_stream_receive_time_histogram and not self._legacy:
      GRPC_CLIENT_STREAM_RECV_HISTOGRAM.labels(
          grpc_type=grpc_type,
          grpc_service=grpc_service_name,
          grpc_method=grpc_method_name).observe(max(default_timer() - start, 0))

    return response_iterator
