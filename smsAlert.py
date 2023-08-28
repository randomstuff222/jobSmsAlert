import email, smtplib, ssl
from providers import PROVIDERS
import json
from email.mime.text import MIMEText

def send_sms_via_email(
    number: str, 
    message:str, 
    provider: str, 
    sender_credentials:tuple, 
    subject:str="sent using python", 
    smtp_server="smtp.gmail.com", 
    smtp_port: int = 465
):

    sender_email, email_password = sender_credentials
    receiver_email = f"{number}@{PROVIDERS.get(provider).get('sms')}"

    email_message = MIMEText(message)
    email_message["From"] = sender_email
    email_message["To"] = receiver_email
    email_message["Subject"] = subject


    with smtplib.SMTP_SSL(smtp_server, smtp_port, context=ssl.create_default_context()) as email:
        email.login(sender_email, email_password)
        email.sendmail(sender_email, receiver_email, email_message.as_string())

def get_config():
    config = {}
    with open("config.json") as config:
        config = json.load()
    return config

def smsAlert(g_company:str, jobs:list):
    with open("config.json", "r") as f:
        credentials = json.load(f)
    number = credentials["number"]
    message = f'New Jobs:\n{jobs}'
    provider = credentials["provider"] #needs to be the provider of your phone

    sender_credentials = (credentials["email"], credentials["password"])

    send_sms_via_email(number, message, provider, sender_credentials, subject=g_company)

if __name__ == "__main__":
    smsAlert()