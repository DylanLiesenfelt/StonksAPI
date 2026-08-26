from abc import ABC, abstractmethod

class IndicatorStrategy(ABC):

    @abstractmethod
    def calculate():
        pass

