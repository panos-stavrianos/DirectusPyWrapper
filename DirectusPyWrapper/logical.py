from DirectusPyWrapper.filter_base import FilterBase
from DirectusPyWrapper.logical_operators import LogicalOperators


class Logical(FilterBase):
    def __init__(self, logical_operator: LogicalOperators, *filters: FilterBase):
        self.logical_operator = logical_operator
        self.filters = list(filters)

    def __json__(self):
        params = {self.logical_operator.value: []}
        for f in self.filters:
            params[self.logical_operator.value].append(f)
        return params
