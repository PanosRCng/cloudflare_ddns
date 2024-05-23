import re
import requests
import time

from .Config import Config
from .Logger import Logger



class PublicIPException(Exception):
    def __init__(self, message, *args):
        self.message = message
        super(PublicIPException, self).__init__(self.message, *args) 



class PublicIP:

    DEFAULT_IP = '127.0.0.1'
    IP_REGEX = '(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'

    # this is public for test purposes
    instance = None


    def __init__(self):

        if PublicIP.instance is not None:
            return

        PublicIP.instance = self
        self.__setup()



    @staticmethod
    def __get_instance():

        if PublicIP.instance is None:
            PublicIP()

        return PublicIP.instance


    @staticmethod
    def get():
        return PublicIP.__get_instance().__get()



    def __setup(self):

        self.__ip_regex = re.compile(PublicIP.IP_REGEX)

        config = Config.get('public_ip')

        self.__urls = eval(config['urls'])
        self.__request_timeout = config['request_timeout']
        self.__refresh_every_n_requests = config.get('refresh_every_n_requests', None)
        self.__refresh_every_n_seconds = config.get('refresh_every_n_seconds', None)
        
        if self.__refresh_every_n_requests:
            self.__requests_counter = self.__refresh_every_n_requests - 1

        if self.__refresh_every_n_seconds:
            self.__last_refreshed = self.__refresh_every_n_seconds + 1

        self.__myip = PublicIP.DEFAULT_IP

        self.__myip = self.__get()


    def __get(self):

        if not self.__needs_refresh():
            return self.__myip

        new_ip = None

        for url in self.__urls:

            try:
                new_ip = self.__get_ip(url)
                break
            except Exception as ex:
                Logger.log(__name__, str(ex), type='debug')

        if new_ip is None:
            return self.__myip

        if new_ip != self.__myip:
            Logger.log(__name__, 'public ip changed, {old_ip} -> {new_ip}'.format(old_ip=self.__myip, new_ip=new_ip), type='debug')
            self.__myip = new_ip

        Logger.log(__name__, 'public ip refreshed: {myip}'.format(myip=self.__myip), type='debug')

        return self.__myip


    def __get_ip(self, url):

        response = self.__request_get(url)

        if response.status_code == 200:

            results = self.__ip_regex.findall(response.text)

            if len(results) != 0:
                return results[0]
            
            raise PublicIPException('could not get valid ip from <{response}>'.format(response=response.text))
        
        raise PublicIPException('request failed with status code <{status_code}> and <{reason}>'.format(status_code=response.status_code,
                                                                                                        reason=response.text.strip()))


    def __request_get(self, url):

        Logger.log(__name__, 'requesting GET url <{url}>'.format(url=url), type='debug')

        try:
            return requests.get(url, timeout=self.__request_timeout)
        except Exception as ex:
            Logger.log(__name__, str(ex), type='debug')
            raise PublicIPException('could not request GET <{url}>'.format(url=url))


    def __needs_refresh(self):

        if self.__refresh_every_n_seconds:

            now = time.time()

            if (now - self.__last_refreshed) > self.__refresh_every_n_seconds:
                self.__last_refreshed = now
                return True

        elif self.__refresh_every_n_requests:

            self.__requests_counter += 1

            if (self.__requests_counter % self.__refresh_every_n_requests) == 0:
                return True

        return False