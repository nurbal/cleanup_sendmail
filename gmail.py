import argparse
import json
import os

import smtplib
from email.mime.text import MIMEText


mydir = os.path.dirname(os.path.realpath(__file__))+'/'

def getCrendentials():
    # load the json file containing the credentials
    account_file = mydir+'secrets/gmail/account.json'
    if os.path.exists(account_file):
        with open(account_file, "r") as f:
            creds = json.load(f)
            print(f'Credentials found in {account_file}')
    if not creds:
        print('No credentials found in secrets/gmail/')
    return creds

def sendMessage(creds,target_email, subject, body):
    # send mail
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = creds['sender']
    msg['To'] = target_email
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
       smtp_server.login(creds['sender'], creds['password'])
       smtp_server.sendmail(creds['sender'], target_email, msg.as_string())
    print("Message sent!")






if __name__ == "__main__":
    # used directly, this script will send a test mail to the specified email address
    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("target_email", help="email address to which send a test mail")
    args = parser.parse_args()    

    # send test mail

    creds = getCrendentials()
    sendMessage(creds, args.target_email, 'Test message', 'Hello, World !\n\nThis is a test message.\nIf you receive it everything regarding gmail configuration is ready.')
