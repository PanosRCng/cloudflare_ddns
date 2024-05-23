from datetime import datetime, timezone
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from .Config import Config
from .Logger import Logger



class Email:

    # this is public for test purposes
    instance = None


    # constructor is not intended to be called from outside the module, only fo test purposes
    def __init__(self):

        if Email.instance is not None:
            return

        Email.instance = self
        self.__setup()



    @staticmethod
    def __get_instance():

        if Email.instance is None:
            Email()

        return Email.instance


    @staticmethod
    def send(subject, message, message_mime='plain', group='all'):
        Email.__get_instance().__send(subject, message, message_mime, group)


    @staticmethod
    def smtp_server():
        return Email.__get_instance().__smtp_server()



    def __setup(self):
        
        config = Config.get('email')

        self.__smtp_host = config['smtp']['host']
        self.__smtp_port = config['smtp']['port']
        self.__smtp_timeout = config['smtp']['timeout']
        self.__from = config['from']

        self.__recipients = self.__setup_recipients(config)

        server = self.__smtp_server()

        if server is None:
            Logger.log(__name__, 'could not connect to smtp server - timeout', type='error')


    def __setup_recipients(self, config):

        recipients = {
            'all': []
        }

        for group, members in config['recipients'].items():
            recipients[group] = eval(members)
            recipients['all'] += eval(members)

        recipients['all'] = list(set(recipients['all']))

        return recipients


    def __smtp_server(self):

        try:
            server = smtplib.SMTP(host=self.__smtp_host, port=self.__smtp_port, timeout=self.__smtp_timeout)
            return server
        except Exception as ex:
            Logger.log(__name__, str(ex), type='error')
            return None


    def __send(self, subject, message, message_mime, group):

        server = self.__smtp_server()

        if server is None:
            Logger.log(__name__, 'could not connect to smtp server - timeout', type='error')
            return False

        recipients = self.__get_recipients(group)

        if recipients is None:
            Logger.log(__name__, 'no recipients specified', type='error')
            return False

        now = datetime.utcnow().replace(tzinfo=timezone.utc).strftime("%Y-%m-%d %H:%M:%S %z")

        msg = MIMEMultipart()
        msg['From'] = self.__from
        msg['To'] = ','.join('<{email}>'.format(email=x) for x in recipients)
        msg['Subject'] = "{subject} {now}".format(subject=subject, now=now)
        msg.attach(MIMEText(message, message_mime))

        try:
            server.send_message(msg)
            server.quit()    
        except Exception as ex:
            Logger.log(__name__, str(ex), type='error')



    def __get_recipients(self, group):

        if group not in self.__recipients:
            Logger.log(__name__, 'recipients group <{group}> does not exist'.format(group=group), type='error')

        return self.__recipients[group]