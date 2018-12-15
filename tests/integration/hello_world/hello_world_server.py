import time
from concurrent import futures

import grpc
from prometheus_client import start_http_server

import tests.integration.hello_world.hello_world_pb2 as hello_world_pb2
import tests.integration.hello_world.hello_world_pb2_grpc as hello_world_grpc
from py_grpc_prometheus.prometheus_server_interceptor import PromServerInterceptor

_ONE_DAY_IN_SECONDS = 60 * 60 * 24


class Greeter(hello_world_grpc.GreeterServicer):

  def SayHello(self, request, context):
    return hello_world_pb2.HelloReply(message='Hello, %s!' % request.name)

  def SayHelloUnaryStream(self, request, context):
    for i in range(10):
      yield hello_world_pb2.HelloReply(message='Hello, %s %s!' % (request.name, i))

  def SayHelloStreamUnary(self, request_iterator, context):
    names = ''
    for request in request_iterator:
      names += request.name
    return hello_world_pb2.HelloReply(message='Hello, %s!' % names)

  def SayHelloBidiStream(self, request_iterator, context):
    for request in request_iterator:
      yield hello_world_pb2.HelloReply(message='Hello, %s!' % request.name)


def serve():
  print("Starting py-grpc-promtheus grpc at localhost:50051, metrics at http://localhost:50052")
  server = grpc.server(futures.ThreadPoolExecutor(max_workers=10),
                       interceptors=(PromServerInterceptor(),))
  hello_world_grpc.add_GreeterServicer_to_server(Greeter(), server)
  server.add_insecure_port('[::]:50051')
  server.start()
  start_http_server(50052)
  print("Started py-grpc-promtheus grpc at localhost:50051, metrics at http://localhost:50052")
  try:
    while True:
      time.sleep(_ONE_DAY_IN_SECONDS)
  except KeyboardInterrupt:
    server.stop(0)


if __name__ == '__main__':
  serve()
