from abc import ABC, abstractmethod

class AbstractAPI(ABC):

    @abstractmethod
    def refreshView(self, model, changedKey):
        ...
