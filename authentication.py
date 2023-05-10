from twilio.rest import Client
import json
import ibm_db
import ibm_db_dbi
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class WhatsAppAuthenticator:
    def __init__(self):
        self.bot_sender_number = None
        self.account_sid = None
        self.auth_token = None
        self.load_keys_and_tokens()

    def load_keys_and_tokens(self):
        with open('client_secret.json') as f:
            data = json.load(f)
            api_data = data['api_twilio']
            self.account_sid = api_data['account_sid']
            self.auth_token = api_data['auth_token']
            self.bot_sender_number = api_data['bot_sender_number']

    def connection(self):
        return Client(self.account_sid, self.auth_token)

class EmailAuthenticator:
    def __init__(self):
        self.sender_email = None
        self.password_email = None
        self.receiver_email = None
        self.load_keys_and_tokens()

    def load_keys_and_tokens(self):
        with open('client_secret.json') as f:
            data = json.load(f)
            email_data = data['email']
            self.sender_email = email_data['login']
            self.password_email = email_data['password']
            self.receiver_email = email_data['receiver_email']

class IBMDB2Authenticator:
    def __init__(self):
        self.dsn_driver = None
        self.dsn_database = None
        self.dsn_hostname = None
        self.dsn_port = None
        self.dsn_protocol = None
        self.dsn_uid = None
        self.dsn_pwd = None
        self.dsn_security = None
        self.load_keys_and_tokens()

    def load_keys_and_tokens(self):
        with open('client_secret.json') as f:
            data = json.load(f)
            db_data = data['db']

            self.dsn_driver = db_data['dsn_driver']
            self.dsn_database = db_data['dsn_database']
            self.dsn_hostname = db_data['dsn_hostname']
            self.dsn_port = db_data['dsn_port']
            self.dsn_protocol = db_data['dsn_protocol']
            self.dsn_uid = db_data['dsn_uid']
            self.dsn_pwd = db_data['dsn_pwd']
            self.dsn_security = db_data['dsn_security']

    def connection(self):
        return ibm_db.connect(f"DATABASE={self.dsn_database};HOSTNAME={self.dsn_hostname};PORT={self.dsn_port};PROTOCOL={self.dsn_protocol};UID={self.dsn_uid};PWD={self.dsn_pwd};SECURITY={self.dsn_security};", "", "")