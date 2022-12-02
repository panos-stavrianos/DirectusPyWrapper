from DirectusPyWrapper.filter_base import FilterBase
from DirectusPyWrapper.logical import Logical
from DirectusPyWrapper.logical_operators import LogicalOperators


class _and(Logical):
    def __init__(self, *filters: FilterBase):
        super().__init__(LogicalOperators.And, *filters)
