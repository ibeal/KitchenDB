from abc import ABC, abstractmethod

class controller(ABC):

    @abstractmethod
    def setup():
        ...
        
    @abstractmethod
    def handle(event, values):
        ...
