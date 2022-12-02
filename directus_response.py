import json
import requests


class DirectusResponse:

    def __init__(self, response: requests.Response):
        self.response: requests.Response = response
        try:
            self.json: dict = response.json()
        except json.decoder.JSONDecodeError:
            self.json = {}

    @property
    def item(self) -> dict:
        return None if 'data' not in self.json else self.json['data']

    @property
    def items(self) -> list:
        return None if 'data' not in self.json else self.json['data']

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
    def errors(self) -> dict:
        if self.is_error and 'errors' in self.json:
            return {"errors": self.json['errors'],
                    "response": self.response.__dict__
                    }
