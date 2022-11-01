from functools import reduce

import pytest

from tests.py_grpc_prometheus.utils import get_server_metric
from tests.integration.hello_world import hello_world_pb2


@pytest.mark.parametrize("target_count", [1, 10, 100])
def test_grpc_server_handled_latency_seconds_with_normal(
    target_count, grpc_server, grpc_stub
):  # pylint: disable=unused-argument
    for i in range(target_count):
        grpc_stub.SayHello(hello_world_pb2.HelloRequest(name=str(i)))
    target_metric = get_server_metric("grpc_server_handled_latency_seconds")
    assert target_metric.samples == []


@pytest.mark.parametrize("number_of_res", [1, 10, 100])
def test_grpc_server_handled_latency_seconds_with_unary_stream(
    number_of_res, grpc_server, grpc_stub
):  # pylint: disable=unused-argument
    list(
        grpc_stub.SayHelloUnaryStream(
            hello_world_pb2.MultipleHelloResRequest(
                name="unary stream", res=number_of_res
            )
        )
    )
    target_metric = get_server_metric("grpc_server_handled_latency_seconds")
    # No grpc_server_handled_latency_seconds for streaming response
    assert target_metric.samples == []


@pytest.mark.parametrize("number_of_names", [1, 10, 100])
def test_grpc_server_handled_latency_seconds_with_stream_unary(
    number_of_names, grpc_server, grpc_stub, stream_request_generator
):  # pylint: disable=unused-argument
    grpc_stub.SayHelloStreamUnary(stream_request_generator(number_of_names))
    target_metric = get_server_metric("grpc_server_handled_latency_seconds")
    assert target_metric.samples == []


@pytest.mark.parametrize(
    "number_of_names, number_of_res", [(1, 10), (10, 100), (100, 100)]
)
def test_grpc_server_handled_latency_seconds_with_bidi_stream(
    number_of_names, number_of_res, grpc_server, grpc_stub, bidi_request_generator
):  # pylint: disable=unused-argument
    list(
        grpc_stub.SayHelloBidiStream(
            bidi_request_generator(number_of_names, number_of_res)
        )
    )
    target_metric = get_server_metric("grpc_server_handled_latency_seconds")
    assert target_metric.samples == []


@pytest.mark.parametrize("target_count", [1, 10, 100])
def test_legacy_grpc_server_handled_latency_seconds_with_normal(
    target_count, grpc_legacy_server, grpc_stub
):  # pylint: disable=unused-argument
    for i in range(target_count):
        grpc_stub.SayHello(hello_world_pb2.HelloRequest(name=str(i)))
    target_metric = get_server_metric("grpc_server_handled_latency_seconds")
    assert (
        reduce(
            lambda acc, x: acc if acc > x.value else x.value,
            list(
                filter(
                    lambda x: x.name == "grpc_server_handled_latency_seconds_bucket",
                    target_metric.samples,
                )
            ),
            0,
        )
        == target_count
    )
    assert (
        reduce(
            lambda acc, x: acc if acc > x.value else x.value,
            list(
                filter(
                    lambda x: x.name == "grpc_server_handled_latency_seconds_count",
                    target_metric.samples,
                )
            ),
            0,
        )
        == target_count
    )
    assert (
        reduce(
            lambda acc, x: acc if acc > x.value else x.value,
            list(
                filter(
                    lambda x: x.name == "grpc_server_handled_latency_seconds_sum",
                    target_metric.samples,
                )
            ),
            0,
        )
        > 0
    )


@pytest.mark.parametrize("number_of_res", [1, 10, 100])
def test_legacy_grpc_server_handled_latency_seconds_with_unary_stream(
    number_of_res, grpc_legacy_server, grpc_stub
):  # pylint: disable=unused-argument
    list(
        grpc_stub.SayHelloUnaryStream(
            hello_world_pb2.MultipleHelloResRequest(
                name="unary stream", res=number_of_res
            )
        )
    )
    target_metric = get_server_metric("grpc_server_handled_latency_seconds")
    # No grpc_server_handled_latency_seconds for streaming response
    assert target_metric.samples == []


@pytest.mark.parametrize("number_of_names", [1, 10, 100])
def test_legacy_grpc_server_handled_latency_seconds_with_stream_unary(
    number_of_names, grpc_legacy_server, grpc_stub, stream_request_generator
):  # pylint: disable=unused-argument
    grpc_stub.SayHelloStreamUnary(stream_request_generator(number_of_names))
    target_metric = get_server_metric("grpc_server_handled_latency_seconds")
    assert (
        reduce(
            lambda acc, x: acc if acc > x.value else x.value,
            list(
                filter(
                    lambda x: x.name == "grpc_server_handled_latency_seconds_bucket",
                    target_metric.samples,
                )
            ),
            0,
        )
        == 1
    )
    assert (
        reduce(
            lambda acc, x: acc if acc > x.value else x.value,
            list(
                filter(
                    lambda x: x.name == "grpc_server_handled_latency_seconds_count",
                    target_metric.samples,
                )
            ),
            0,
        )
        == 1
    )
    assert (
        reduce(
            lambda acc, x: acc if acc > x.value else x.value,
            list(
                filter(
                    lambda x: x.name == "grpc_server_handled_latency_seconds_sum",
                    target_metric.samples,
                )
            ),
            0,
        )
        > 0
    )


@pytest.mark.parametrize(
    "number_of_names, number_of_res", [(1, 10), (10, 100), (100, 100)]
)
def test_legacy_grpc_server_handled_latency_seconds_with_bidi_stream(
    number_of_names,
    number_of_res,
    grpc_legacy_server,
    grpc_stub,
    bidi_request_generator,
):  # pylint: disable=unused-argument
    list(
        grpc_stub.SayHelloBidiStream(
            bidi_request_generator(number_of_names, number_of_res)
        )
    )
    target_metric = get_server_metric("grpc_server_handled_latency_seconds")
    assert target_metric.samples == []
