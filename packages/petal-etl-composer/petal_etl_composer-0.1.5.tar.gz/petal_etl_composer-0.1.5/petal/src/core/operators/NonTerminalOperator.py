from abc import ABC

from core.operators.Sink import Sink
from core.operators.Source import Source


class NonTerminalOperator(Source, Sink, ABC):
    def __init__(self, operator_id: str):
        super().__init__(operator_id)
