from abc import ABC, abstractmethod

class data_container(ABC):

    @abstractmethod
    def getID(self):
        ...

    @abstractmethod
    def getName(self):
        ...

    @abstractmethod
    def getIngs(self):
        ...

    @abstractmethod
    def guts(self):
        ...
