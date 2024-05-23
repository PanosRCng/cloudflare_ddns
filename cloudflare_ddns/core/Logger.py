import os
from datetime import datetime, timezone

from .Config import Config



class Logger:


    __instance = None


    def __init__(self):

        if Logger.__instance is not None:
            return

        Logger.__instance = self
        self.__setup()


    @staticmethod
    def __get_instance():

        if Logger.__instance is None:
            Logger()

        return Logger.__instance


    @staticmethod
    def log(source, message, type='info'):
        return Logger.__get_instance().__log(source, message, type)


    def __setup(self):
        self.__log_level = Config.get('LOGS')['log_level']
        self.__logfile_enabled = Config.get('LOGS')['logfile_enabled']
        self.__json_format_enabled = Config.get('LOGS')['json_format_enabled']
        self.__email_enabled = Config.get('LOGS')['email_enabled']
        self.__logfilepath = Config.get('LOGS')['directory'] + '/cloudflare_ddns.log'

        if self.__logfile_enabled:
            self.__logfile = open(self.__logfilepath, 'a')
            self.__check_rotation()


    def __check_rotation(self):

        filesize = round(os.path.getsize(self.__logfilepath) / 2048, 2)

        if filesize < Config.get('LOGS')['max_size_MB']:
            return

        os.rename(self.__logfilepath, self.__logfilepath.replace('.log', '_1.log'))
        self.__logfile = open(self.__logfilepath, 'a')



    def __log(self, source, message, type):

        log_line = ''

        if type == 'debug' and self.__log_level == 'debug':
            log_line = self.__log_line(source, message, type)
        elif type == 'info':
            log_line = self.__log_line(source, message, type)
        elif type == 'warning':
            log_line = self.__log_line(source, message, type)
        elif type == 'error':
            log_line = self.__log_line(source, message, type)

            if self.__email_enabled:
                if 'mail' not in source:
                    import cloudflare_ddns.core.Email as mEmail
                    mEmail.Email.send(subject='error', message=log_line, group='admin')

        if log_line == '':
            return

        if self.__logfile_enabled:
            self.__logfile.write(log_line + "\n")
            self.__logfile.flush()
            self.__check_rotation()

        print(log_line, flush=True)


    def __log_line(self, source, message, type):

        if self.__json_format_enabled:
            return '{{"timestamp": "{timestamp}", "type": "{type}", "source": "{source}", "message": "{message}"}}'.format(timestamp=self.__time_stamp(), source=source, message=message, type=type.upper())
        else:
            return '[{timestamp}] [{type}] {source}: {message}'.format(timestamp=self.__time_stamp(), source=source, message=message, type=type.upper())


    def __time_stamp(self):
        return datetime.utcnow().replace(tzinfo=timezone.utc).strftime("%Y-%m-%d %H:%M:%S %z")


