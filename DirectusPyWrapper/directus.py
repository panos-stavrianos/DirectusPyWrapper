import datetime
from typing import Optional

import requests

from DirectusPyWrapper.directus_request import DirectusRequest


class BearerAuth(requests.auth.AuthBase):
    def __init__(self, token):
        self.token = token

    def __call__(self, r):
        r.headers["authorization"] = f"Bearer {self.token}"
        return r


class Directus:
    def __init__(self, url, email=None, password=None, static_token=None):
        self.expires = None
        self.expiration_time = None
        self.refresh_token = None
        self.url: str = url
        self.email: str = email
        self.password: str = password
        self.static_token: str = static_token
        self._token: Optional[str] = None
        self.session = requests.Session()
        if self.static_token:
            self.token = self.static_token
            return
        if self.email and self.password:
            self.login()

    @property
    def token(self):
        return self._token

    @token.setter
    def token(self, token):
        self._token = token
        self.session.auth = BearerAuth(self._token)

    def login(self):
        if self.static_token:
            self._token = self.static_token
            return

        url = f'{self.url}/auth/login'
        payload = {
            'email': self.email,
            'password': self.password
        }

        response = self.session.post(url, json=payload)
        self._token = response.json()['data']['access_token']
        self.refresh_token = response.json()['data']['refresh_token']
        self.expires = response.json()['data']['expires']  # in milliseconds
        self.expiration_time: datetime.datetime = datetime.datetime.now() + datetime.timedelta(
            milliseconds=self.expires)
        self.session.auth = BearerAuth(self._token)

    def items(self, collection):
        return DirectusRequest(self, collection)

    def read_me(self):
        return DirectusRequest(self, "directus_users").read_one("me")

    def logout(self):
        url = f'{self.url}/auth/logout'
        response = self.session.post(url)
        self.session.auth = None
        self.session.close()
        return response.status_code == 204

    def __enter__(self):
        return self

    def __exit__(self, *args):
        # Exception handling here
        self.logout()
