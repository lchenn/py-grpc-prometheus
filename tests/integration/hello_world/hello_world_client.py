import logging
import sys
import time

import grpc
from prometheus_client import start_http_server

import tests.integration.hello_world.hello_world_pb2 as hello_world_pb2
import tests.integration.hello_world.hello_world_pb2_grpc as hello_world_grpc
from py_grpc_prometheus.prometheus_client_interceptor import PromClientInterceptor

_ONE_DAY_IN_SECONDS = 60 * 60 * 24
_LOGGER = logging.getLogger(__name__)


def call_server():
    channel = grpc.intercept_channel(
        grpc.insecure_channel("localhost:50051"), PromClientInterceptor()
    )
    stub = hello_world_grpc.GreeterStub(channel)

    # Call the unary-unary.
    for _ in range(5):
        try:
            response = stub.SayHello(hello_world_pb2.HelloRequest(name="Unary"))
            _LOGGER.info("Unary response: %s", response.message)
            _LOGGER.info("")
        except grpc.RpcError:
            _LOGGER.error("Got an exception from server")

    # Call the unary stream.
    _LOGGER.info("Running Unary Stream client")
    response_iter = stub.SayHelloUnaryStream(
        hello_world_pb2.HelloRequest(name="unary stream")
    )
    _LOGGER.info("Response for Unary Stream")
    for response in response_iter:
        _LOGGER.info("Unary Stream response item: %s", response.message)
    _LOGGER.info("")

    # Call the stream_unary.
    try:
        _LOGGER.info("Running Stream Unary client")
        response = stub.SayHelloStreamUnary(generate_requests("Stream Unary"))
        _LOGGER.info("Stream Unary response: %s", response.message)
        _LOGGER.info("")
    except grpc.RpcError:
        _LOGGER.error("Got an exception from server")

    # Call stream & stream.
    _LOGGER.info("Running Bidi Stream client")
    response_iter = stub.SayHelloBidiStream(generate_requests("Bidi Stream"))
    for response in response_iter:
        _LOGGER.info("Bidi Stream response item: %s", response.message)
    _LOGGER.info("")


def generate_requests(name):
    for i in range(10):
        yield hello_world_pb2.HelloRequest(name="%s %s" % (name, i))


def run():
    logging.basicConfig(level=logging.INFO, format="%(asctime)-15s %(message)s")
    _LOGGER.info("Starting py-grpc-promtheus hello word server")
    call_server()
    start_http_server(50053)
    _LOGGER.info(
        "Started py-grpc-promtheus client, metrics is located at http://localhost:50053"
    )
    try:
        while True:
            time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        sys.exit()


if __name__ == "__main__":
    run()
