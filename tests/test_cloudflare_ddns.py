import pytest
import json

from cloudflare_ddns.core.Config import Config
from cloudflare_ddns.cloudflare_ddns import main
from cloudflare_ddns.core.Logger import Logger
from cloudflare_ddns.core.PublicIP import PublicIP
from cloudflare_ddns.core.CloudflareZonesApi import CloudflareZonesApi, CloudflareZonesApiException



@pytest.fixture()
def patch_config_get(monkeypatch):

    def mock_get(*args, **kwargs):
        return {
                "name": "mydomain",
                "type": "A",
                "zone_name": "mydomain"
        }

    monkeypatch.setattr(Config, 'get', mock_get)


@pytest.fixture()
def patch_logger_log(monkeypatch):

    def mock_log(*args, **kwargs):
        return {}

    monkeypatch.setattr(Logger, 'log', mock_log)


@pytest.fixture()
def patch_publicip_get_fail(monkeypatch):

    def mock_get(*args, **kwargs):
        return '127.0.0.1'

    monkeypatch.setattr(PublicIP, 'get', mock_get)


@pytest.fixture()
def patch_publicip_get_success(monkeypatch):

    def mock_get(*args, **kwargs):
        return '0.0.0.0'

    monkeypatch.setattr(PublicIP, 'get', mock_get)


@pytest.fixture()
def patch_publicip_get_success_new_ip(monkeypatch):

    def mock_get(*args, **kwargs):
        return '0.0.0.1'

    monkeypatch.setattr(PublicIP, 'get', mock_get)


@pytest.fixture()
def patchCloudflareZonesApi_retrieve_zone_id_fail(monkeypatch):

    def mock_retrieve_zone_id(*args, **kwargs):
        raise CloudflareZonesApiException('could not retrieve zone_id')

    monkeypatch.setattr(CloudflareZonesApi, 'retrieve_zone_id', mock_retrieve_zone_id)


@pytest.fixture()
def patchCloudflareZonesApi_retrieve_zone_id_success(monkeypatch):

    def mock_retrieve_zone_id(*args, **kwargs):
        return 'b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1'

    monkeypatch.setattr(CloudflareZonesApi, 'retrieve_zone_id', mock_retrieve_zone_id)


@pytest.fixture()
def patchCloudflareZonesApi_retrieve_dns_records_fail(monkeypatch):

    def mock_retrieve_dns_records(*args, **kwargs):
        raise CloudflareZonesApiException('could not retrieve dns records')

    monkeypatch.setattr(CloudflareZonesApi, 'retrieve_dns_records', mock_retrieve_dns_records)


@pytest.fixture()
def patchCloudflareZonesApi_retrieve_dns_records_dont_exist(monkeypatch):

    def mock_retrieve_dns_records(*args, **kwargs):

        with open('tests/data/retrieve_dns_records_response_200_dont_exist.json') as file:
            return json.loads(file.read())

    monkeypatch.setattr(CloudflareZonesApi, 'retrieve_dns_records', mock_retrieve_dns_records)


@pytest.fixture()
def patchCloudflareZonesApi_retrieve_dns_records_success(monkeypatch):

    def mock_retrieve_dns_records(*args, **kwargs):

        with open('tests/data/retrieve_dns_records_response_200.json') as file:
            return json.loads(file.read())

    monkeypatch.setattr(CloudflareZonesApi, 'retrieve_dns_records', mock_retrieve_dns_records)


@pytest.fixture()
def patchCloudflareZonesApi_overwrite_dns_records_fail(monkeypatch):

    def mock_overwrite_dns_record(*args, **kwargs):
        raise CloudflareZonesApiException('could not overwrite dns record')

    monkeypatch.setattr(CloudflareZonesApi, 'overwrite_dns_record', mock_overwrite_dns_record)


@pytest.fixture()
def patchCloudflareZonesApi_overwrite_dns_records_success(monkeypatch):

    def mock_overwrite_dns_record(*args, **kwargs):
        return True

    monkeypatch.setattr(CloudflareZonesApi, 'overwrite_dns_record', mock_overwrite_dns_record)






def test_public_ip_get_fail(patch_publicip_get_fail, patch_logger_log):

    with pytest.raises(SystemExit) as system_exit_info:
        main()
    assert system_exit_info.value.code == 1



def test_retrieve_zone_id_fail(patchCloudflareZonesApi_retrieve_zone_id_fail, patch_publicip_get_success, patch_logger_log):

    with pytest.raises(SystemExit) as system_exit_info:
        main()
    assert system_exit_info.value.code == 1


def test_retrieve_dns_records_fail(patchCloudflareZonesApi_retrieve_dns_records_fail, patchCloudflareZonesApi_retrieve_zone_id_success, patch_publicip_get_success, patch_logger_log):

    with pytest.raises(SystemExit) as system_exit_info:
        main()
    assert system_exit_info.value.code == 1


def test_locate_dns_record_fail(patchCloudflareZonesApi_retrieve_dns_records_dont_exist, patchCloudflareZonesApi_retrieve_zone_id_success, patch_publicip_get_success, patch_logger_log, patch_config_get):

    with pytest.raises(SystemExit) as system_exit_info:
        main()
    assert system_exit_info.value.code == 1


def test_overwrite_dns_record_fail(patchCloudflareZonesApi_overwrite_dns_records_fail, patchCloudflareZonesApi_retrieve_dns_records_success, patchCloudflareZonesApi_retrieve_zone_id_success, patch_publicip_get_success_new_ip, patch_logger_log, patch_config_get):

    with pytest.raises(SystemExit) as system_exit_info:
        main()
    assert system_exit_info.value.code == 1


def test_overwrite_dns_record_success_uptodate(patchCloudflareZonesApi_overwrite_dns_records_success, patchCloudflareZonesApi_retrieve_dns_records_success, patchCloudflareZonesApi_retrieve_zone_id_success, patch_publicip_get_success, patch_logger_log, patch_config_get):

    with pytest.raises(SystemExit) as system_exit_info:
        main()
    assert system_exit_info.value.code == 0


def test_overwrite_dns_record_success_outdated(patchCloudflareZonesApi_overwrite_dns_records_success, patchCloudflareZonesApi_retrieve_dns_records_success, patchCloudflareZonesApi_retrieve_zone_id_success, patch_publicip_get_success_new_ip, patch_logger_log, patch_config_get):

    with pytest.raises(SystemExit) as system_exit_info:
        main()
    assert system_exit_info.value.code == 0
