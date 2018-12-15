import time

import grpc
from prometheus_client import start_http_server

import tests.integration.hello_world.hello_world_pb2 as hello_world_pb2
import tests.integration.hello_world.hello_world_pb2_grpc as hello_world_grpc
from py_grpc_prometheus.prometheus_client_interceptor import PromClientInterceptor

_ONE_DAY_IN_SECONDS = 60 * 60 * 24


def call_server():
  channel = grpc.intercept_channel(grpc.insecure_channel('localhost:50051'),
                                   PromClientInterceptor())
  stub = hello_world_grpc.GreeterStub(channel)

  # Call the unary-unary.
  response = stub.SayHello(hello_world_pb2.HelloRequest(name='Unary'))
  print("Unary response: " + response.message)
  print("")

  # Call the unary stream.
  print("Running Unary Stream client")
  response_iter = stub.SayHelloUnaryStream(hello_world_pb2.HelloRequest(name='unary stream'))
  print("Response for Unary Stream")
  print(response_iter)
  for response in response_iter:
    print("Unary Stream response item: " + response.message)
  print("")

  # Call the stream_unary.
  print("Running Stream Unary client")
  response = stub.SayHelloStreamUnary(generate_requests("Stream Unary"))
  print("Stream Unary response: " + response.message)
  print("")

  # Call stream & stream.
  print("Running Bidi Stream client")
  response_iter = stub.SayHelloBidiStream(generate_requests("Bidi Stream"))
  for response in response_iter:
    print("Bidi Stream response item: " + response.message)
  print("")


def generate_requests(name):
  for i in range(10):
    yield hello_world_pb2.HelloRequest(name='%s %s' % (name, i))


def run():
  print("Started py-grpc-promtheus client, metrics is located at http://localhost:50053")
  call_server()
  start_http_server(50053)
  try:
    while True:
      time.sleep(_ONE_DAY_IN_SECONDS)
  except KeyboardInterrupt:
    quit(0)


if __name__ == '__main__':
  run()
