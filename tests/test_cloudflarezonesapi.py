import pytest
import requests
import json

from cloudflare_ddns.core.Config import Config
from cloudflare_ddns.core.Logger import Logger
from cloudflare_ddns.core.CloudflareZonesApi import CloudflareZonesApi, CloudflareZonesApiException



@pytest.fixture()
def config_test_default(monkeypatch):
    monkeypatch.setattr(Config, "config_path", 'tests/data/test_cloudflarezonesapi_config.json')
    monkeypatch.setattr(Config, "env_path", None)
    CloudflareZonesApi()
    yield
    Config.instance = None
    CloudflareZonesApi.instance = None


@pytest.fixture()
def patch_logger_log(monkeypatch):

    def mock_log(*args, **kwargs):
        return {}

    monkeypatch.setattr(Logger, 'log', mock_log)


@pytest.fixture()
def patch_requests_get_zone_id_response_200_exists(monkeypatch):

    class Response:
        status_code = 200

        with open('tests/data/retrieve_zone_id_response_200_exists.json') as file:
            contents = json.loads(file.read())

        def json(self):
            return self.contents

    def mock_get(*args, **kwargs):
        return Response()

    monkeypatch.setattr(requests, 'get', mock_get)


@pytest.fixture()
def patch_requests_get_zone_id_response_200_dont_exist(monkeypatch):

    class Response:
        status_code = 200

        with open('tests/data/retrieve_zone_id_response_200_dont_exist.json') as file:
            contents = json.loads(file.read())

        def json(self):
            return self.contents

    def mock_get(*args, **kwargs):
        return Response()

    monkeypatch.setattr(requests, 'get', mock_get)


@pytest.fixture()
def patch_requests_get_dns_records_response_200(monkeypatch):

    class Response:
        status_code = 200

        with open('tests/data/retrieve_dns_records_response_200.json') as file:
            contents = json.loads(file.read())

        def json(self):
            return self.contents

    def mock_get(*args, **kwargs):
        return Response()

    monkeypatch.setattr(requests, 'get', mock_get)


@pytest.fixture()
def patch_requests_get_dns_records_response_404(monkeypatch):

    class Response:
        status_code = 404
        text = '{"result":null,"success":false,"errors":[{"code":7003,"message":"Could not route to /client/v4/zones/asfdsafd/dns_records, perhaps your object identifier is invalid?"}],"messages":[]}'

    def mock_get(*args, **kwargs):
        return Response()

    monkeypatch.setattr(requests, 'get', mock_get)


@pytest.fixture()
def patch_requests_put_overwrite_dns_record_response_200(monkeypatch):

    class Response:
        status_code = 200

        with open('tests/data/overwrite_dns_records_response_200.json') as file:
            contents = json.loads(file.read())

        def json(self):
            return self.contents

    def mock_put(*args, **kwargs):
        return Response()

    monkeypatch.setattr(requests, 'put', mock_put)


@pytest.fixture()
def patch_requests_put_overwrite_dns_record_exception(monkeypatch):

    def mock_put(*args, **kwargs):
        raise ValueError('something went wrong')

    monkeypatch.setattr(requests, 'put', mock_put)




def test_singleton_can_be_instatiated(patch_logger_log, config_test_default):
    assert CloudflareZonesApi.instance != None


def test_singleton_cannot_be_instantiated_twice(patch_logger_log, config_test_default):

    instance_1 = CloudflareZonesApi.instance
    CloudflareZonesApi()
    instance_2 = CloudflareZonesApi.instance

    assert instance_1 is instance_2


def test_retrieve_zone_id_200_exists(patch_requests_get_zone_id_response_200_exists, patch_logger_log, config_test_default):

    assert CloudflareZonesApi.retrieve_zone_id('mydomain') == 'b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1'


def test_retrieve_zone_id_200_dont_exist(patch_requests_get_zone_id_response_200_dont_exist, patch_logger_log, config_test_default):

    try:
        CloudflareZonesApi.retrieve_zone_id('mydomain')
    except CloudflareZonesApiException:
        assert True


def test_locate_dns_record_200(patch_requests_get_dns_records_response_200, patch_logger_log, config_test_default):

    dns_records = CloudflareZonesApi.retrieve_dns_records(zone_id='b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1')

    assert dns_records['result'][0]['content'] == '0.0.0.0'


def test_locate_dns_record_404(patch_requests_get_dns_records_response_404, patch_logger_log, config_test_default):

    try:
        CloudflareZonesApi.retrieve_dns_records(zone_id='WRONG_ZONE_ID')
    except CloudflareZonesApiException:
        assert True


def test_overwrite_dns_record_200(patch_requests_put_overwrite_dns_record_response_200, patch_logger_log, config_test_default):

    res = CloudflareZonesApi.overwrite_dns_record(zone_id='', dns_record_id='', dns_record={})

    assert res is True


def test_overwrite_dns_record_exception(patch_requests_put_overwrite_dns_record_exception, patch_logger_log, config_test_default):

    try:
        CloudflareZonesApi.overwrite_dns_record(zone_id='', dns_record_id='', dns_record={})
    except CloudflareZonesApiException:
        assert True

