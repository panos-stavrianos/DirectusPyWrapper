from enum import Enum


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
