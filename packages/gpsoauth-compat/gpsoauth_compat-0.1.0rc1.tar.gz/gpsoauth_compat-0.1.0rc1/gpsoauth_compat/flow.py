from __future__ import annotations

from gpsoauth import exchange_token
from .credentials import GPCredentialsBase


class GPLogin:
    def __init__(self, credentials, client_config):
        self.credentials = credentials
        self.client_config = client_config
        self._master_token = client_config.get('master_token')

    @classmethod
    def from_oauth_token(cls, token: str, scopes) -> GPLogin:
        response = exchange_token(email='', android_id='', token=token)
        if 'Error' in response:
            raise ValueError
        if 'Token' not in response:
            raise ValueError

        master_token = response.get('Token')
        email = response.get('Email')
        first_name = response.get('firstName')
        last_name = response.get('lastName')
        client_config = {
            'master_token': master_token,
            'email': email,
            'first_name': first_name,
            'last_name': last_name
            }

        credentials = GPCredentialsBase.from_master_token(master_token, scopes)
        return cls(credentials, client_config)

    @classmethod
    def from_master_token(cls, master_token, scopes):
        #TODO: obtain user info & validate token
        client_config = {
            'master_token': master_token,
            'email': '',
            'first_name': '',
            'last_name': ''
            }
        credentials = GPCredentialsBase.from_master_token(master_token, scopes)
        return cls(credentials, client_config)
