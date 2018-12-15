#!/usr/bin/env python
from setuptools import find_packages
from setuptools import setup

setup(name='py_grpc_prometheus',
      version='0.0.2',
      description='Python gRPC Prometheus Interceptors',
      author='Lin Chen',
      author_email='linchen04@gmail.com',
      install_requires=[
          'setuptools==39.0.1',
          'protobuf==3.5.2',
          'grpcio==1.10.0',
          'prometheus_client==0.3.0'
      ],
      url='',
      packages=find_packages(exclude=["tests.*", "tests"]),
     )
