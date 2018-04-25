import grpc

from .rpc import http_proxy_pb2_grpc


def GrpcStub(host):
    # open a gRPC channel
    channel = grpc.insecure_channel(host)

    # create a stub (client)
    stub = http_proxy_pb2_grpc.HttpProxyStub(channel)

    return stub
