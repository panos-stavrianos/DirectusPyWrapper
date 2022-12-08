from __future__ import annotations

import datetime
from typing import Optional

import requests

from DirectusPyWrapper.directus_request import DirectusRequest
from DirectusPyWrapper.directus_response import DirectusResponse
from DirectusPyWrapper.models import User


class BearerAuth(requests.auth.AuthBase):
    def __init__(self, token: str):
        self.token = token

    def __call__(self, r):
        r.headers["authorization"] = f"Bearer {self.token}"
        return r


class Directus:
    def __init__(self, url, email=None, password=None, token=None, refresh_token=None,
                 session: requests.Session = None):
        self.expires = None
        self.expiration_time = None
        self.refresh_token = refresh_token
        self.url: str = url
        self._token: Optional[str] = None
        self.email = email
        self.password = password
        self.static_token = token
        self.session = session or requests.Session()
        self.auth = BearerAuth(self._token)
        self.token = self.static_token or None
        self._user: User | None = None
        if self.email and self.password:
            self.login()

    def items(self, collection):
        return DirectusRequest(self, collection)

    def read_me(self):
        return DirectusRequest(self, "directus_users").read_one("me")

    def __enter__(self):
        return self

    @property
    def token(self):
        return self._token

    @token.setter
    def token(self, token):
        self._token = token
        self.auth = BearerAuth(self._token)

    @property
    def user(self):
        if self._user is None:
            self._user = User(**self.read_me().item)
        return self._user

    def login(self):
        if self.static_token:
            self._token = self.static_token
            return

        url = f'{self.url}/auth/login'
        payload = {
            'email': self.email,
            'password': self.password
        }

        r = self.session.post(url, json=payload)
        response = DirectusResponse(r)
        self._token = response.item['access_token']
        self.refresh_token = response.item['refresh_token']
        self.expires = response.item['expires']  # in milliseconds
        self.expiration_time: datetime.datetime = datetime.datetime.now() + datetime.timedelta(
            milliseconds=self.expires)
        self.auth = BearerAuth(self._token)

    def refresh(self):
        url = f'{self.url}/auth/refresh'
        payload = {
            'refresh_token': self.refresh_token,
            "mode": "json"
        }
        r = self.session.post(url, json=payload)
        response = DirectusResponse(r)
        self._token = response.item['access_token']
        self.refresh_token = response.item['refresh_token']
        self.expires = response.item['expires']

    def logout(self):
        url = f'{self.url}/auth/logout'
        response = self.session.post(url)
        self.session.auth = None
        return response.status_code == 200

    def close_session(self):
        self.session.close()

    def __exit__(self, *args):
        # Exception handling here
        self.logout()
