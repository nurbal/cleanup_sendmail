import argparse
import json
import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import google.auth
from email.message import EmailMessage
import base64

def getSecretFile(directory='secrets/gmail/'):
    files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
    for file in files:
        if file.endswith('.json'):
            return directory+file
    return None


def getCrendentials():
    creds = None
    token_path = "secrets/gmail/token.json"
    SCOPES = ["https://www.googleapis.com/auth/gmail.compose"]

    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        # scan secrets/gmail/ to retrieve secret key
        secret_file = getSecretFile()
        if secret_file is None:
            print('No clientID found in secrets/gmail/')
            exit(1) 

        flow = InstalledAppFlow.from_client_secrets_file(secret_file, SCOPES)
        creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(token_path, "w") as token:
            token.write(creds.to_json())

    return creds

def sendMessage(creds,target_email, subject, body):
    """Create and insert a draft email.
    Print the returned draft's message and id.
    Returns: Draft object, including draft id and message meta data.

    Load pre-authorized user credentials from the environment.
    TODO(developer) - See https://developers.google.com/identity
    for guides on implementing OAuth2 for the application.
    """
    try:
        # create gmail api client
        service = build("gmail", "v1", credentials=creds)

        message = EmailMessage()

        message.set_content(body)

        message["To"] = target_email
        message["From"] = "noreply@mila.quebec"
        message["Subject"] = subject

        # encoded message
        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

        create_message = {"message": {"raw": encoded_message}}
        # pylint: disable=E1101
        send_message = (
            service.users()
            .messages()
            .send(userId="me", body=create_message)
            .execute()
        )
        # send_message = (
        #     service.users()
        #     .drafts()
        #     .create(userId="me", body=create_message)
        #     .execute()
        # )

    except HttpError as error:
        print(f"An error occurred: {error}")
        send_message = None

    return send_message





if __name__ == "__main__":
    # used directly, this script will send a test mail to the specified email address
    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("target_email", help="email address to which send a test mail")

    args = parser.parse_args()    

    # scan secrets/gmail/ to retrieve clientID and secret key
    secret_file = getSecretFile()
    if secret_file is None:
        print('No clientID found in secrets/gmail/')
        exit(1) 
    else:
        print(f"secret file found: {secret_file}")

    # # print secret_file
    # print(f"clientID: {secret_file}")

    # send test mail

    creds = getCrendentials()
    sendMessage(creds, args.target_email, 'Test message', 'Hello, World !\n\nThis is a test message.\nIf you receive it everything regarding gmail configuration is ready.')
