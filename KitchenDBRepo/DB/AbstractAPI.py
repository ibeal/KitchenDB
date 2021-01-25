from abc import ABC, abstractmethod

class AbstractAPI(ABC):

    @abstractmethod
    def search(self, query):
        ...

    @abstractmethod
    def exists(self, key):
        ...

    @abstractmethod
    def lookup(self, key):
        ...

    @abstractmethod
    def delete(self, key):
        ...

    @abstractmethod
    def save(self, item):
        ...
