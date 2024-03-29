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
        if self.token is not None:
            r.headers["authorization"] = f"Bearer {self.token}"
        return r


def parse_translations(all_translations: list[dict]) -> dict[str, dict[str, str]] | None:
    if all_translations is None or not all_translations:
        return None

    return {translations['key']: {translation['languages_code']: translation['translation']
                                  for translation in
                                  translations['translations']} for translations in all_translations}


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

    def collection(self, directus_collection) -> DirectusRequest:
        assert directus_collection.Config.collection is not None
        return self.items(directus_collection.Config.collection, directus_collection)

    def items(self, collection, directus_collection=None) -> DirectusRequest:
        return DirectusRequest(self, collection, directus_collection)

    def read_me(self):
        return DirectusRequest(self, "directus_users").read("me")

    def read_settings(self):
        return DirectusRequest(self, "directus_settings").read(method='get')

    def update_settings(self, data):
        return DirectusRequest(self, "directus_settings").update_one(None, data)

    def read_translations(self) -> dict[str, dict[str, str]]:
        items = self.items("translations").fields('key', 'translations.languages_code',
                                                  'translations.translation').read().items
        return parse_translations(items)

    def download_file(self, file_id):
        return self.session.get(f'{self.url}/assets/{file_id}')

    def create_translations(self, keys: list[str]):
        return self.items("translations").create_many([{"key": key} for key in keys])

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
        self.token = response.item['access_token']
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
        self.close_session()
