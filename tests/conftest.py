import pytest
from _server import StubServer

from hiapi_seedance import Seedance


@pytest.fixture
def server():
    s = StubServer()
    try:
        yield s
    finally:
        s.stop()


@pytest.fixture
def client(server):
    return Seedance(api_key="sk-test", base_url=server.base_url, timeout=5.0)
