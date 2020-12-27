from abc import ABC, abstractmethod

class controller(ABC):

    @abstractmethod
    def setup(self):
        ...

    @abstractmethod
    def handle(self, event, values):
        ...
