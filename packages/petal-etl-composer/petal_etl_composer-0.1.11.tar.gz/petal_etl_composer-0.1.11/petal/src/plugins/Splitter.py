import copy
from typing import Any, Iterable

from petal.src.core.operators.NonTerminalOperator import NonTerminalOperator


class Splitter(NonTerminalOperator):
    def __init__(self, operator_id):
        super().__init__(operator_id)

    def process(self, data: Any) -> Iterable[Any]:
        return copy.deepcopy(data)
