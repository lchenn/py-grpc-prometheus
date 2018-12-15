import unittest
from unittest import TestCase

from py_grpc_prometheus import grpc_method
from py_grpc_prometheus.grpc_method import GrpcMethod


class TestGrpcMethod(TestCase):

  def __init__(self, *args, **kwargs):
    unittest.TestCase.__init__(self, *args, **kwargs)

  def test_get_method_type(self):
    self.assertEqual(GrpcMethod.get_method_type(True, True), grpc_method.BIDI_STREAMING)
    self.assertEqual(GrpcMethod.get_method_type(True, False), grpc_method.CLIENT_STREAMING)
    self.assertEqual(GrpcMethod.get_method_type(False, True), grpc_method.SERVER_STREAMING)
    self.assertEqual(GrpcMethod.get_method_type(False, False), grpc_method.UNARY)


if __name__ == "__main__":
  unittest.main()
