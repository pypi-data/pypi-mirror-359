# GPSOauth Compatibility Layer 
`gpsoauth` compatibility layer for `google-api-python-client`

Use Google Play Services authentication provided by [gpsoauth](https://github.com/simon-weber/gpsoauth) with public Google APIs provided by [google-api-python-client](https://github.com/googleapis/google-api-python-client).

Google Play Services authenticated accounts are sometimes given special permissions, even on public APIs. This project thus aims to reduce the need for maintaining scattered wrappers around privileged private APIs when public APIs give the same privileges with `gpsoauth`-provided tokens.

This mini-library aims to pose as the many Android apps that Google allows access to its API. Unfortunately, not all API scopes are available for consumption on Android applications. A comprehensive list of unavailable scopes is being worked on. In the meantime, consider using Google's recommended flow of authentication for the scopes that are unavailable on any of Google's Android applications.

## Usage

See https://github.com/rukins/gpsoauth-java#receiving-an-authentication-token for obtaining your account's oauth token.

```python
from googleapiclient.discovery import build
from gpsoauth_compat import GPLogin

SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly']
API_SERVICE_NAME = 'drive'
API_VERSION = 'v3'

OAUTH_TOKEN = 'SECRET_GOES_HERE'

flow = GPLogin.from_oauth_token(OAUTH_TOKEN, SCOPES)
# alternatively use the following line if you already have authenticated before
# flow = GPLogin.from_master_token(MASTER_TOKEN, SCOPES)

credentials = flow.credentials
service = build(API_SERVICE_NAME, API_VERSION, credentials = credentials)
print(service.files().list().execute())
```

> [!WARNING]
> To log-out and disable this token and all its derivatives, visit https://myaccount.google.com/device-activity and navigate to your desired account. From there, you will find a device with a small caption on it saying "Android device". Click on it and log out from it.
>
> It may be associated with your browser's login session, so you will have to use a private/ incognito browsing session to access that webpage and log yourself out from your main browser. You may have to log in into your main browser again to continue using your account on it.
