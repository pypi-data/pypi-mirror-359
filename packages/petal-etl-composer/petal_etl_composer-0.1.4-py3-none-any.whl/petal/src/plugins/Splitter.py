import copy
from typing import Any, Iterable

from core.operators.NonTerminalOperator import NonTerminalOperator


class Splitter(NonTerminalOperator):
    def __init__(self, node_id):
        super().__init__(node_id)

    def process(self, data: Any) -> Iterable[Any]:
        return copy.deepcopy(data)
