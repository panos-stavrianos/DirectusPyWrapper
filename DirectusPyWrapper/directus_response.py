from __future__ import annotations

import json
from typing import Any, TypeVar, List

import requests
from pydantic import BaseModel, parse_obj_as, TypeAdapter


class DirectusResponse:
    T = TypeVar("T", bound=BaseModel)

    def __init__(self, response: requests.Response, query: dict = None, collection: Any = None):
        self.response: requests.Response = response
        self.query: dict = query
        self.collection: Any = collection
        try:
            self.json: dict = response.json()
            if self.is_error:
                raise DirectusException(self)
        except json.decoder.JSONDecodeError:
            self.json = {}

    def _parse_item_as_dict(self) -> dict:
        if isinstance(self.json['data'], list):
            return self.json['data'][0]
        return self.json['data']

    def _parse_item_as_object(self, T) -> T:
        return T(**self._parse_item_as_dict())

    def _parse_items_as_dict(self) -> list[dict]:
        if isinstance(self.json['data'], list):
            return self.json['data']
        return [self.json['data']]

    def _parse_items_as_objects(self, T) -> list[T]:
        return TypeAdapter(List[T]).validate_python(self._parse_items_as_dict())

    @property
    def item(self) -> dict[Any, Any] | None | Any:  # noqa
        if 'data' not in self.json or self.json['data'] in [None, [], {}]:
            return None
        if self.collection:
            return self._parse_item_as_object(self.collection)
        return self._parse_item_as_dict()

    def item_as(self, T) -> T | None:  # noqa
        item_data = self._parse_item_as_dict()
        return None if item_data is None else T(**item_data)

    def item_as_dict(self) -> dict | None:  # noqa
        if 'data' not in self.json or self.json['data'] in [None, [], {}]:
            return None
        return self._parse_item_as_dict()

    @property
    def items(self) -> list[dict[Any, Any]] | None | Any:  # noqa
        if 'data' not in self.json or self.json['data'] in [None, [], {}]:
            return None
        if self.collection:
            return self._parse_items_as_objects(self.collection)
        return self._parse_items_as_dict()

    def items_as(self, T) -> list[T] | None:  # noqa
        items_data = self._parse_items_as_dict()
        return None if items_data is None else parse_obj_as(List[T], items_data)

    def items_as_dict(self) -> list[dict] | None:  # noqa
        if 'data' not in self.json or self.json['data'] in [None, [], {}]:
            return None
        return self._parse_items_as_dict()

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
        self.status_code = response.status_code
        self.message = None
        self.code = None
        if len(response.errors) > 0 and 'message' in response.errors[0] and 'extensions' in response.errors[
            0] and 'code' in response.errors[0]['extensions']:
            self.message = response.errors[0]['message']
            self.code = response.errors[0]['extensions']['code']

    def __str__(self):
        return f'{self.code}: {self.message}'
