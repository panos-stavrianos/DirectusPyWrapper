from __future__ import annotations
import json_fix

from DirectusPyWrapper._and import _and
from DirectusPyWrapper.directus_response import DirectusResponse
from DirectusPyWrapper.filter import Filter
from DirectusPyWrapper.logical import Logical
from DirectusPyWrapper.logical_operators import LogicalOperators
from DirectusPyWrapper.operators import Operators


class DirectusRequest:

    def __init__(self, directus: "Directus", collection: str):
        json_fix.fix_it()
        self.directus: "Directus" = directus
        self.collection: str = collection
        self.params: dict = {}

    @property
    def uri(self):
        if "directus_" in self.collection:
            return f"{self.directus.url}/{self.collection.replace('directus_', '')}"
        return f'{self.directus.url}/items/{self.collection}'

    def fields(self, *fields):
        self.params['fields'] = ','.join(fields)
        return self

    def filter(self, operator: Operators = Operators.Equals,
               logical_operator: LogicalOperators = LogicalOperators.And,
               **filters):

        filter_param = Filter(operator, logical_operator, **filters)
        if 'filter' in self.params:
            if isinstance(self.params['filter'], Logical):
                self.params['filter'].filters.append(filter_param)
            else:
                self.params['filter'] = _and(self.params['filter'], filter_param)
        else:
            self.params['filter'] = filter_param
        return self

    def filters(self, filters: list[Logical]):
        if 'filter' in self.params:
            self.params['filter'].filters.extend(filters)
        else:
            self.params['filter'] = _and(*filters)
        return self

    def sort(self, field, asc=True):
        if 'sort' not in self.params:
            self.params['sort'] = []
        self.params['sort'].append(f'{"" if asc else "-"}{field}')
        return self

    def page(self, page: int = 1):
        self.params['page'] = page
        return self

    def limit(self, limit: int = -1):
        self.params['limit'] = limit
        return self

    def offset(self, offset: int = 0):
        self.params['offset'] = offset
        return self

    def include_count(self):
        self.params['meta'] = '*'
        return self

    def read_one(self, id: int | str) -> DirectusResponse:
        response = self.directus.session.get(f'{self.uri}/{id}')
        return DirectusResponse(response)

    def read_many(self) -> DirectusResponse:
        response = self.directus.session.request("search", self.uri, json={"query": self.params})
        return DirectusResponse(response, self.params)

    def create_one(self, item: dict) -> DirectusResponse:
        response = self.directus.session.post(self.uri, json=item)
        return DirectusResponse(response)

    def create_many(self, items: list[dict]) -> DirectusResponse:
        response = self.directus.session.post(self.uri, json=items)
        return DirectusResponse(response)

    def update_one(self, id: int | str, item: dict) -> DirectusResponse:
        response = self.directus.session.patch(f'{self.uri}/{id}', json=item)
        return DirectusResponse(response)

    def update_many(self, ids: list[int | str], items) -> DirectusResponse:
        payload = {
            "keys": ids,
            "data": items
        }
        response = self.directus.session.patch(self.uri, json=payload)
        return DirectusResponse(response)

    def delete_one(self, id: int | str) -> DirectusResponse:
        response = self.directus.session.delete(f'{self.uri}/{id}')
        return DirectusResponse(response)

    def delete_many(self, ids: list[int | str]) -> DirectusResponse:
        response = self.directus.session.delete(self.uri, json=ids)
        return DirectusResponse(response)
