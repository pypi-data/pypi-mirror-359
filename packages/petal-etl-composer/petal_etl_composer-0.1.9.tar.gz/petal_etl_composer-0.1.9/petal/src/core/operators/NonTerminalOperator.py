from abc import ABC, abstractmethod
from typing import Iterable, Any

from petal.src.core.operators.Sink import Sink
from petal.src.core.operators.Source import Source


class NonTerminalOperator(Source, Sink, ABC):
    def __init__(self, operator_id: str):
        super().__init__(operator_id)

    @abstractmethod
    def process(self, data: Iterable[Any]) -> Iterable[Any]:
        pass
