from abc import ABC, abstractmethod

class view(ABC):

    @abstractmethod
    def refreshView(model, changedKey):
        ...
