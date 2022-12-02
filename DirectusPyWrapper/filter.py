from DirectusPyWrapper.filter_base import FilterBase
from DirectusPyWrapper.logical_operators import LogicalOperators
from DirectusPyWrapper.operators import Operators


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

