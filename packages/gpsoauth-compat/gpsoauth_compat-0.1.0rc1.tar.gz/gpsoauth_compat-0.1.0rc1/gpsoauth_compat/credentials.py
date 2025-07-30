from __future__ import annotations

from datetime import datetime

from google.auth.credentials import Credentials, Scoped
from google.auth.exceptions import RefreshError
from gpsoauth import perform_oauth

"""
Todo:
    - Make comprehensive map of all Google apps on Android and their allowed scopes from the public discovery API  
    - Manage multiple tokens in one Credentials object to use different apps to avoid restricted scopes
References:
    https://google-auth.readthedocs.io/en/stable/_modules/google/auth/credentials.html
    https://github.com/rukins/gpsoauth-java/blob/master/README.md
    https://github.com/simon-weber/gpsoauth
"""

class GPCredentialsBase(Credentials, Scoped):
    def __init__(self):
        super().__init__()
        self.master_token = None

    def requires_scopes(self) -> bool:
        # gpsoauth-based authentication always requires scopes to be specified
        return True

    def copy(self, scopes):
        """actual copying with addition of scopes"""
        pass

    def with_scopes(self, scopes=None, default_scopes=None) -> GPCredentialsBase:
        """disabled scope addition functionality for compatibility with google-api-client"""
        return self

    @classmethod
    def from_master_token(cls, master_token, scopes) -> GPCredentialsBase:
        credentials = cls()
        credentials.master_token = master_token
        credentials._default_scopes = scopes
        credentials._scopes = scopes
        credentials.refresh()
        return credentials

    def refresh(self, request = None) -> None:
        # request is not needed

        if self.expiry is not None and not self.expired:
            return

        if len(self.scopes) == 0:
            raise RefreshError
        if self.master_token is None:
            raise RefreshError

        scope_str = f'oauth2:{" ".join(set(self._scopes))}'
        response = perform_oauth(email='', master_token=self.master_token, android_id='', service=scope_str, app='com.google.android.apps.docs', client_sig='38918a453d07199354f8b19af05ec6562ced5788')

        if 'Error' in response:
            raise RefreshError
        if 'Expiry' not in response:
            raise RefreshError
        if 'Auth' not in response:
            raise RefreshError
        if 'grantedScopes' not in response:
            raise RefreshError

        self.token = response['Auth']
        self.expiry = datetime.fromtimestamp(float(response['Expiry']))
