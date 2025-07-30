import copy
from typing import Any, Callable, Iterable

from petal.src.core.operators.NonTerminalOperator import NonTerminalOperator


class Mapper(NonTerminalOperator):
    def __init__(self, operator_id: str, mapping_func: Callable):
        super().__init__(operator_id)
        self.mapping_func = mapping_func

    def process(self, data: Iterable[Any]) -> Iterable[Any]:
        return map(self.mapping_func, copy.deepcopy(data))
