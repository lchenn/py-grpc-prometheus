# py-grpc-prometheus

Instrument library to provide prometheus metrics similar to:

- https://github.com/grpc-ecosystem/java-grpc-prometheus
- https://github.com/grpc-ecosystem/go-grpc-prometheus


## Status
Currently, the library has the parity metrics with the Java and Go library.

### Server side:
- grpc_server_started_total
- grpc_server_handled_total
- grpc_server_handled_latency_seconds
- grpc_server_msg_received_total
- grpc_server_msg_sent_total

### Client side:
- grpc_client_started_total
- grpc_client_completed
- grpc_client_completed_latency_seconds
- grpc_client_msg_sent_total
- grpc_client_msg_received_total

## How to use

```
pip install py-grpc-prometheus
```

## Client side:
Client metrics monitoring is done by intercepting the gPRC channel.

```python
import grpc
from py_grpc_prometheus.prometheus_client_interceptor import PromClientInterceptor

channel = grpc.intercept_channel(grpc.insecure_channel('server:6565'),
                                         PromClientInterceptor())  
# Start an end point to expose metrics.
start_http_server(metrics_port)
```

## Server side:
Server metrics are exposed by adding the interceptor when the gRPC server is started. Take a look at
`tests/integration/hello_world/hello_world_client.py` for the complete example.

```python
import grpc
from concurrent import futures
from py_grpc_prometheus.prometheus_server_interceptor import PromServerInterceptor
from prometheus_client import start_http_server
```

Start the gRPC server with the interceptor, take a look at
`tests/integration/hello_world/hello_world_server.py` for the complete example.

```python
server = grpc.server(futures.ThreadPoolExecutor(max_workers=10),
                         interceptors=(PromServerInterceptor(),))
# Start an end point to expose metrics.
start_http_server(metrics_port)
```

## How to run and test
1. Run the testing server

```bash
python -m tests.integration.hello_world.hello_world_sever
```

2. Run the testing client
```bash
python -m tests.integration.hello_world.hello_world_client
```

3. Open http://localhost:50052 for the server side metrics
4. Open http://localhost:50053 for the client side metrics

## TODO:
- Unit test with https://github.com/census-instrumentation/opencensus-python/blob/master/tests/unit/trace/ext/grpc/test_server_interceptor.py

## Reference
- https://grpc.io/grpc/python/grpc.html
- https://github.com/census-instrumentation/opencensus-python/blob/master/opencensus/trace/ext/grpc/utils.py
- https://github.com/opentracing-contrib/python-grpc/blob/b4bdc7ce81fa75ede00f7c6bcf5dab8fae47332a/grpc_opentracing/grpcext/grpc_interceptor/server_interceptor.py
