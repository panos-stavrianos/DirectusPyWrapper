from __future__ import annotations

import json
from typing import Any

import requests


class DirectusResponse:
    def __init__(self, response: requests.Response, query: dict = None):
        self.response: requests.Response = response
        self.query: dict = query
        try:
            self.json: dict = response.json()
            if self.is_error:
                raise DirectusException(self)
        except json.decoder.JSONDecodeError:
            self.json = {}

    @property
    def item(self) -> dict[Any, Any] | None | Any:
        if 'data' not in self.json:
            return None
        if not isinstance(self.json['data'], list):
            return self.json['data']
        return None if len(self.json['data']) == 0 else self.json['data'][0]

    @property
    def first(self) -> dict:
        return self.item

    @property
    def items(self) -> list[Any] | None | Any:
        if 'data' not in self.json:
            return None
        if isinstance(self.json['data'], list):
            if len(self.json['data']) == 0:
                return None
            return self.json['data']
        else:
            return [self.json['data']]

    @property
    def total_count(self) -> int:
        if 'meta' in self.json and 'total_count' in self.json['meta']:
            return self.json['meta']['total_count']

    @property
    def filtered_count(self) -> int:
        if 'meta' in self.json and 'filter_count' in self.json['meta']:
            return self.json['meta']['filter_count']

    @property
    def status_code(self) -> int:
        return self.response.status_code

    @property
    def is_success(self) -> bool:
        return self.status_code in [200, 201, 204, 304]

    @property
    def is_error(self) -> bool:
        return not self.is_success

    @property
    def errors(self) -> list:
        if self.is_error and 'errors' in self.json:
            return self.json['errors']


class DirectusException(Exception):
    def __init__(self, response: DirectusResponse):
        self.response = response
        self.messages = response.errors

    def __str__(self):
        return ''.join(f"{error['extensions']['code']}:\n{error['message']}\n " for error in self.messages)
