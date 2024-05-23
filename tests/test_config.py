import pytest
from cloudflare_ddns.core.Config import Config



@pytest.fixture()
def config_test_default(monkeypatch):
    monkeypatch.setattr(Config, "config_path", 'tests/data/test_config.json')
    monkeypatch.setattr(Config, "env_path", None)
    Config()
    yield
    Config.instance = None

@pytest.fixture()
def config_test_override(monkeypatch):
    monkeypatch.setattr(Config, "config_path", 'tests/data/test_config.json')
    monkeypatch.setattr(Config, "env_path", 'tests/data/test_env')
    Config()
    yield
    Config.instance = None



def test_singleton_can_be_instatiated(config_test_default):
    assert Config.instance != None


def test_singleton_cannot_be_instantiated_twice(config_test_default):

    instance_1 = Config.instance
    Config()
    instance_2 = Config.instance

    assert instance_1 is instance_2


def test_get_nonexistent_key(config_test_default):
    assert Config.get('nonexistent_key') is None


def test_get_defaults(config_test_default):

    assert Config.get('test')['string'] == 'a string'
    assert Config.get('test')['number'] == 100
    assert Config.get('test')['boolean'] == True
    
    string_list = eval(Config.get('test')['list_of_strings'])
    assert type(string_list) is type([])
    for string in string_list:
        assert type(string) is str


def test_override_defaults_from_env_file(config_test_override):

    assert Config.get('test')['string'] == 'a string from env'
    assert Config.get('test')['number'] == 200
    assert Config.get('test')['boolean'] == False

    string_list = eval(Config.get('test')['list_of_strings'])
    assert type(string_list) is type([])
    for string in string_list:
        assert type(string) is str

