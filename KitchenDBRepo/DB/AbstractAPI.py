from abc import ABC, abstractmethod

class AbstractAPI(ABC):

    @abstractmethod
    def search(self, query):
        ...
