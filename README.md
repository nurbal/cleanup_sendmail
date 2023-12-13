# cleanup_sendmail

This project requires 2 set of secrets:

## LDAP
Put the .crt and .key files in `secrets/ldap/`.

## Gmail API secrets
Put the .json file from your Goolge project in `secrets/gmail/`.

The name should be in the form `client_secret_<clientID>.json` where clientID is something like `123456789012-123something456something789else0.apps.googleusercontent.com`
The program will just scan the folder to retrieve these informations from the first json file found in `secrets/gmail/`.

You also need a `token.json` file. If no token is available, you can run `python gmail.py <your mail address>` to generate this token file and send you a test mail.