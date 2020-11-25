from abc import ABC, abstractmethod

class controller(ABC):

    @abstractmethod
    def handle(event, values):
        ...
