# cleanup_sendmail

This project requires 2 set of secrets:

## LDAP
Put the .crt and .key files in `secrets/ldap/`.

## Gmail account & app password

You will need to create an "app password" for the used gmail account.
To create it, go to google account settings->security->2-step-verification->app password (bottom of the page)

Then put the account details in secrets/gmail/account.json :
```
{
    "sender": "mailbot.accountname@mila.quebec",
    "password": "lorem ipsum"
}

```
