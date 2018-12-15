# py-grpc-prometheus

Instrument library to provide prometheus metrics similar to:

- https://github.com/grpc-ecosystem/java-grpc-prometheus
- https://github.com/grpc-ecosystem/go-grpc-prometheus

Currently, the library supports only the unary calls, and it exposes the following metrics:

## Server side:
- grpc_server_started_total
- ~~grpc_server_handled_total~~
- grpc_server_handled_latency_seconds
- ~~grpc_server_msg_received_total~~
- ~~grpc_server_msg_sent_total~~

## Client side:
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
Server metrics are exposed by adding the interceptor when the gRPC server is started.

```python
import grpc
from concurrent import futures
from py_grpc_prometheus.prometheus_server_interceptor import PromServerInterceptor
from prometheus_client import start_http_server
```

Start the gRPC server with the interceptor

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


## Reference
https://grpc.io/grpc/python/grpc.html
