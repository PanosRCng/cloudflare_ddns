import os
import re
import json
from dotenv import load_dotenv



class Config:

    # these are public for test purposes
    instance = None
    config_path='cloudflare_ddns/config.json'
    env_path='envs/.env'


    # constructor is not intended to be called from outside the module, only fo test purposes
    def __init__(self):

        if Config.instance is not None:
            return

        Config.instance = self
        self.__setup()


    @staticmethod
    def __get_instance():

        if Config.instance is None:
            Config()

        return Config.instance


    @staticmethod
    def get(key):
        return Config.__get_instance().__get(key)



    def __setup(self):
        self.__configs = self.__load()


    def __load(self):

        load_dotenv(dotenv_path=Config.env_path)

        with open(Config.config_path) as file:

            config_str = file.read()

            for setting in re.findall('[?<=\[].*[?=\]]', config_str):
                config_str = self.__set_value(config_str, setting, self.__find_value(setting))

            contents = json.loads(config_str)

            return contents


    def __get(self, key):

        if key in self.__configs:
            return self.__configs[key]

        return None


    def __find_value(self, setting):

        default = None

        setting = setting[1:-1]
        parts = setting.split(',')
        key = parts[0].replace('"', '')
                
        if len(parts) > 1:
            default = parts[1].replace('"', '').strip()

        value = os.getenv(key, default)

        return value


    def __set_value(self, config_str, setting, value):

        if value is None:
            config_str = config_str.replace(setting, 'null')
            return config_str

        if value in ['true', 'false']:
            config_str = config_str.replace(setting, 'true') if (value == 'true') else config_str.replace(setting, 'false')
            return config_str

        if value.isdigit():
            config_str = config_str.replace(setting, value)
            return config_str

        config_str = config_str.replace(setting, '"' + value + '"')

        return config_str
