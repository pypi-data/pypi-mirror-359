import copy
from typing import Any, Callable, Iterable

from petal.src.core.operators.NonTerminalOperator import NonTerminalOperator


class Filter(NonTerminalOperator):
    def __init__(self, operator_id: str, filter_func: Callable):
        super().__init__(operator_id)
        self.filter_func = filter_func

    def process(self, data: Iterable[Any]) -> Iterable[Any]:
        return filter(self.filter_func, copy.deepcopy(data))
