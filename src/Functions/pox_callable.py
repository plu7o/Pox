from abc import ABC, abstractmethod

class PoxCallable(ABC):
    @abstractmethod
    def call(self, interpreter, arguments: list) -> object:
        pass

    @abstractmethod
    def arity(self) -> int:
        pass
