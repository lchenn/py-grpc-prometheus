import logging
import requests

import pytest
from prometheus_client.parser import text_string_to_metric_families

import tests.integration.hello_world.hello_world_pb2 as hello_world_pb2

LOGGER = logging.getLogger(__name__)

@pytest.mark.parametrize(
    "target_count",
    [
        1, 10, 100
    ]
)
def test_grpc_server_handled(target_count, grpc_server, grpc_stub):  # pylint: disable=unused-argument
  for i in range(target_count):
    response = grpc_stub.SayHello(hello_world_pb2.HelloRequest(name=str(i)))
    assert response.message == "Hello, {}!".format(i)
  metrics = list(text_string_to_metric_families(requests.get("http://localhost:50052/metrics", timeout=5).text))
  target_metric = list(filter(lambda x: x.name == "grpc_server_handled", metrics))
  assert len(target_metric) == 1
  assert target_metric[0].samples[0].value == target_count
