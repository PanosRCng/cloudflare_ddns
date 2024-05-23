import pytest
import requests

from cloudflare_ddns.core.Config import Config
from cloudflare_ddns.core.Logger import Logger
from cloudflare_ddns.core.PublicIP import PublicIP



@pytest.fixture()
def config_test_default(monkeypatch):
    monkeypatch.setattr(Config, "config_path", 'tests/data/test_publicip_config.json')
    monkeypatch.setattr(Config, "env_path", None)
    PublicIP()
    yield
    Config.instance = None
    PublicIP.instance = None


@pytest.fixture()
def patch_logger_log(monkeypatch):

    def mock_log(*args, **kwargs):
        return {}

    monkeypatch.setattr(Logger, 'log', mock_log)


@pytest.fixture()
def patch_requests_get_200(monkeypatch):

    class Response:
        status_code = 200
        text = '0.0.0.0'

    def mock_get(*args, **kwargs):
        return Response()

    monkeypatch.setattr(requests, 'get', mock_get)


@pytest.fixture()
def patch_requests_get_200_not_valid(monkeypatch):

    class Response:
        status_code = 200
        text = 'not.valid.ip.0'

    def mock_get(*args, **kwargs):
        return Response()

    monkeypatch.setattr(requests, 'get', mock_get)


@pytest.fixture()
def patch_requests_get_500(monkeypatch):

    class Response:
        status_code = 500
        text = 'internal server error'

    def mock_get(*args, **kwargs):
        return Response()

    monkeypatch.setattr(requests, 'get', mock_get)


@pytest.fixture()
def patch_requests_get_exception(monkeypatch):

    def mock_get(*args, **kwargs):
        raise ValueError('something went wrong')

    monkeypatch.setattr(requests, 'get', mock_get)



def test_singleton_can_be_instatiated(patch_requests_get_200, patch_logger_log, config_test_default):
    assert PublicIP.instance != None


def test_singleton_cannot_be_instantiated_twice(patch_requests_get_200, patch_logger_log, config_test_default):

    instance_1 = PublicIP.instance
    PublicIP()
    instance_2 = PublicIP.instance

    assert instance_1 is instance_2


def test_get_public_ip_200(patch_requests_get_200, patch_logger_log, config_test_default):

    ip = PublicIP.get()

    assert ip == '0.0.0.0'


def test_get_public_ip_200_not_valid_fallback_to_localhost(patch_requests_get_200_not_valid, patch_logger_log, config_test_default):

    ip = PublicIP.get()

    assert ip == '127.0.0.1'


def test_get_public_ip_500_fallback_to_localhost(patch_requests_get_500, patch_logger_log, config_test_default):

    ip = PublicIP.get()

    assert ip == '127.0.0.1'


def test_get_public_ip_exception_fallback_to_localhost(patch_requests_get_exception, patch_logger_log, config_test_default):

    ip = PublicIP.get()

    assert ip == '127.0.0.1'

