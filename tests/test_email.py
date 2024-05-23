import pytest
import smtplib
from cloudflare_ddns.core.Config import Config
from cloudflare_ddns.core.Logger import Logger
from cloudflare_ddns.core.Email import Email



@pytest.fixture()
def config_test_default(monkeypatch):
    monkeypatch.setattr(Config, "config_path", 'tests/data/test_email_config.json')
    monkeypatch.setattr(Config, "env_path", None)
    Email()
    yield
    Config.instance = None
    Email.instance = None


@pytest.fixture()
def patch_logger_log(monkeypatch):

    def mock_log(*args, **kwargs):
        return {}

    monkeypatch.setattr(Logger, 'log', mock_log)


@pytest.fixture()
def patch_smtplib_smtp_fail(monkeypatch):

    def mock_smtp(*args, **kwargs):
        return None

    monkeypatch.setattr(smtplib, 'SMTP', mock_smtp)


@pytest.fixture()
def patch_smtplib_smtp_success(monkeypatch):

    def mock_smtp(*args, **kwargs):
        return {}

    monkeypatch.setattr(smtplib, 'SMTP', mock_smtp)



def test_singleton_can_be_instatiated(patch_smtplib_smtp_success, config_test_default):
    assert Email.instance != None


def test_singleton_cannot_be_instantiated_twice(patch_smtplib_smtp_success, config_test_default):

    instance_1 = Email.instance
    Email()
    instance_2 = Email.instance

    assert instance_1 is instance_2


def test_email_smtp_server_fail(patch_smtplib_smtp_fail, patch_logger_log, config_test_default):
    assert Email.smtp_server() is None


def test_email_smtp_server_success(patch_smtplib_smtp_success, config_test_default):
    assert Email.smtp_server() == {}
