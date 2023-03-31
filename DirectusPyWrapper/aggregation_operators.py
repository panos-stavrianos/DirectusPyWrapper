from enum import Enum


class AggregationOperators(str, Enum):
    Count = "count"
    CountDistinct = "countDistinct"
    CountAll = "countAll"
    Sum = "sum"
    SumDistinct = "sumDistinct"
    Average = "avg"
    AverageDistinct = "avgDistinct"
    Minimum = "min"
    Maximum = "max"
