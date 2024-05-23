import requests
import json

from .Config import Config
from .Logger import Logger



class CloudflareZonesApiException(Exception):
    def __init__(self, message, *args):
        self.message = message
        super(CloudflareZonesApiException, self).__init__(self.message, *args) 



class CloudflareZonesApi:

    # these are public for test purposes
    instance = None


    # constructor is not intended to be called from outside the module, only fo test purposes
    def __init__(self):

        if CloudflareZonesApi.instance is not None:
            return

        CloudflareZonesApi.instance = self
        self.__setup()


    @staticmethod
    def __get_instance():

        if CloudflareZonesApi.instance is None:
            CloudflareZonesApi()

        return CloudflareZonesApi.instance


    def __setup(self):
        self.__config = Config.get('cloudflare_zones_api')


    @staticmethod
    def retrieve_zone_id(zone_name):
        return CloudflareZonesApi.__get_instance().__retrieve_zone_id(zone_name)


    @staticmethod
    def retrieve_dns_records(zone_id):
        return CloudflareZonesApi.__get_instance().__retrieve_dns_records(zone_id)


    @staticmethod
    def overwrite_dns_record(zone_id, dns_record_id, dns_record):
        return CloudflareZonesApi.__get_instance().__overwrite_dns_record(zone_id, dns_record_id, dns_record)



    def __retrieve_zone_id(self, zone_name):

        url = '{base_url}/{version}/zones?name={zone_name}'.format(base_url=self.__config['base_url'],
                                                                   version=self.__config['version'],
                                                                   zone_name=zone_name)

        response = self.__request_get(url)

        if response.status_code != 200:

            Logger.log(__name__, 'request failed with status code <{status_code}> and <{reason}>'.format(status_code=response.status_code,
                                                                                                        reason=response.text.strip()), type='debug')

            raise CloudflareZonesApiException('could not retrieve zone_id for name <{zone_name}>'.format(zone_name=zone_name))

        try:
            return response.json()['result'][0]['id']
        except Exception as ex:
            Logger.log(__name__, str(ex), type='debug')
            raise CloudflareZonesApiException('could not retrieve zone_id for name <{zone_name}>'.format(zone_name=zone_name))



    def __retrieve_dns_records(self, zone_id):

        url = '{base_url}/{version}/zones/{zone_id}/dns_records'.format(base_url=self.__config['base_url'],
                                                                        version=self.__config['version'],
                                                                        zone_id=zone_id)

        response = self.__request_get(url)

        if response.status_code == 200:
            return response.json()
                
        Logger.log(__name__, 'request failed with status code <{status_code}> and <{reason}>'.format(status_code=response.status_code,
                                                                                                     reason=response.text.strip()), type='debug')

        raise CloudflareZonesApiException('could not retrieve dns records')


    def __overwrite_dns_record(self, zone_id, dns_record_id, dns_record):

        url = '{base_url}/{version}/zones/{zone_id}/dns_records/{dns_record_id}'.format(base_url=self.__config['base_url'],
                                                                                        version=self.__config['version'],
                                                                                        zone_id=zone_id,
                                                                                        dns_record_id=dns_record_id)

        response = self.__request_put(url, dns_record)

        if response.status_code != 200:
            raise CloudflareZonesApiException('request failed with status code <{status_code}> and <{reason}>'.format(status_code=response.status_code,
                                                                                                                     reason=response.text.strip()))

        return True



    def __request_get(self, url):

        Logger.log(__name__, 'requesting GET url <{url}>'.format(url=url), type='debug')

        headers = {
            'Authorization': 'Bearer {api_token}'.format(api_token=self.__config['api_token']),
            'Content-Type': 'application/json'
        }

        try:
            return requests.get(url, headers=headers, timeout=self.__config['request_timeout'])
        except Exception as ex:
            Logger.log(__name__, str(ex), type='debug')
            raise CloudflareZonesApiException('could not request GET <{url}>'.format(url=url))


    def __request_put(self, url, dns_record):

        Logger.log(__name__, 'requesting PUT url: <{url}>'.format(url=url), type='debug')

        headers = {
            'Authorization': 'Bearer {api_token}'.format(api_token=self.__config['api_token']),
            'Content-Type': 'application/json'
        }

        try:
            return requests.put(url, headers=headers, timeout=self.__config['request_timeout'], data=json.dumps(dns_record))
        except Exception as ex:
            Logger.log(__name__, str(ex), type='debug')
            raise CloudflareZonesApiException('could not request PUT <{url}>'.format(url=url))

