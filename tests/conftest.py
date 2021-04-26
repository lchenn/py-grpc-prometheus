from concurrent import futures
import threading

import pytest
import grpc
from prometheus_client import exposition, registry

from py_grpc_prometheus.prometheus_client_interceptor import PromClientInterceptor
from py_grpc_prometheus.prometheus_server_interceptor import PromServerInterceptor
from tests.integration.hello_world import hello_world_pb2_grpc as hello_world_grpc
from tests.integration.hello_world.hello_world_server import Greeter
from tests.integration.hello_world import hello_world_pb2

def start_prometheus_server(port, prom_registry=registry.REGISTRY):
  app = exposition.make_wsgi_app(prom_registry)
  httpd = exposition.make_server(
      "",
      port,
      app,
      exposition.ThreadingWSGIServer,
      handler_class=exposition._SilentHandler  # pylint: disable=protected-access
  )
  t = threading.Thread(target=httpd.serve_forever)
  t.start()
  return httpd

@pytest.fixture(scope='function')
def grpc_server():
  prom_registry = registry.CollectorRegistry(auto_describe=True)
  server = grpc.server(futures.ThreadPoolExecutor(max_workers=2),
                       interceptors=(
                           PromServerInterceptor(
                               enable_handling_time_histogram=True,
                               registry=prom_registry
                           ),
                       ))
  hello_world_grpc.add_GreeterServicer_to_server(Greeter(), server)
  server.add_insecure_port("[::]:50051")
  server.start()
  prom_server = start_prometheus_server(50052, prom_registry)

  yield server
  server.stop(0)
  prom_server.shutdown()
  prom_server.server_close()

@pytest.fixture(scope='function')
def grpc_stub():
  prom_registry = registry.CollectorRegistry(auto_describe=True)
  channel = grpc.intercept_channel(grpc.insecure_channel("localhost:50051"),
                                   PromClientInterceptor(registry=prom_registry))
  stub = hello_world_grpc.GreeterStub(channel)
  prom_server = start_prometheus_server(50053, prom_registry)

  yield stub

  channel.close()
  prom_server.shutdown()

@pytest.fixture(scope="module")
def stream_request_generator():
  def _generate_requests(number_of_names):
    for i in range(number_of_names):
      yield hello_world_pb2.HelloRequest(name="{}".format(i))
  return _generate_requests

@pytest.fixture(scope="module")
def bidi_request_generator():
  def _generate_bidi_requests(number_of_names, number_of_res):
    for i in range(number_of_names):
      yield hello_world_pb2.MultipleHelloResRequest(name="{}".format(i), res=number_of_res)
  return _generate_bidi_requests
