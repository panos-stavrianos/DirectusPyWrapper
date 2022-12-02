import json
from abc import ABC, abstractmethod


class FilterBase(ABC):
    def __str__(self):
        return json.dumps(self.__json__())

    def __repr__(self):
        return self.__str__()

    @abstractmethod
    def __json__(self):
        pass
