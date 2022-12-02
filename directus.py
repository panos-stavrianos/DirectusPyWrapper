import datetime
import json
from abc import abstractmethod, ABC
from enum import Enum
from typing import Optional

import requests


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
        self.token: Optional[str] = None
        self.session = requests.Session()
        self.login()

    def login(self):
        if self.static_token:
            self.token = self.static_token
            return

        url = f'{self.url}/auth/login'
        payload = {
            'email': self.email,
            'password': self.password
        }

        response = self.session.post(url, json=payload)
        self.token = response.json()['data']['access_token']
        self.refresh_token = response.json()['data']['refresh_token']
        self.expires = response.json()['data']['expires']  # in milliseconds
        self.expiration_time: datetime.datetime = datetime.datetime.now() + datetime.timedelta(
            milliseconds=self.expires)
        self.session.auth = BearerAuth(self.token)

    def items(self, collection):
        from directus_request import DirectusRequest

        return DirectusRequest(self, collection)

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


class Operators(str, Enum):
    Equals = "_eq"
    NotEqual = "_neq"
    LessThan = "_lt"
    LessThanOrEqual = "_lte"
    GreaterThan = "_gt"
    GreaterThanOrEqual = "_gte"
    In = "_in"
    NotIn = "_nin"
    Null = "_null"
    NotNull = "_nnull"
    Contains = "_contains"
    NotContains = "_ncontains"
    StartsWith = "_starts_with"
    NotStartsWith = "_nstarts_with"
    EndsWith = "_ends_with"
    NotEndsWith = "_nends_with"
    Between = "_between"
    NotBetween = "_nbetween"
    Empty = "_empty"
    NotEmpty = "_nempty"
    Intersects = "_intersects"
    NotIntersects = "_nintersects"
    IntersectsBBox = "_intersects_bbox"
    NotIntersectsBBox = "_nintersects_bbox"


class LogicalOperators(str, Enum):
    And = "_and"
    Or = "_or"


class FilterBase(ABC):
    def __str__(self):
        return json.dumps(self.__json__())

    def __repr__(self):
        return self.__str__()

    @abstractmethod
    def __json__(self):
        pass


class Filter(FilterBase):
    def __init__(self, operator: Operators,
                 logical_operator: LogicalOperators = LogicalOperators.And,
                 **filters):
        self.operator = operator
        self.logical_operator = logical_operator
        self.filters = filters

    def __json__(self):
        params = {self.logical_operator: []}

        for key, value in self.filters.items():
            if value is None:
                if self.operator == Operators.Equals:
                    self.operator = Operators.Null
                elif self.operator == Operators.NotEqual:
                    self.operator = Operators.NotNull
            if "." in key:
                fields = key.split(".")
                if len(fields) > 2:
                    raise NotImplementedError("Filtering depth is limited to 2")
                params[self.logical_operator].append({fields[0]: {fields[1]: {self.operator: value}}})
            else:
                params[self.logical_operator].append({key: {self.operator: value}})

        # if there is only one filter, remove the logical operator
        if len(params[self.logical_operator]) == 1:
            params = params[self.logical_operator][0]

        return params


class Logical(FilterBase):
    def __init__(self, logical_operator: LogicalOperators, *filters: FilterBase):
        self.logical_operator = logical_operator
        self.filters = list(filters)

    def __json__(self):
        params = {self.logical_operator.value: []}
        for f in self.filters:
            params[self.logical_operator.value].append(f)
        return params


class _and(Logical):
    def __init__(self, *filters: FilterBase):
        super().__init__(LogicalOperators.And, *filters)


class _or(Logical):
    def __init__(self, *filters: FilterBase):
        super().__init__(LogicalOperators.Or, *filters)
