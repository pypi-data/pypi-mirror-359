from typing import Any, Iterable, Callable
from functools import reduce

from petal.src.core.operators.NonTerminalOperator import NonTerminalOperator


class Joiner(NonTerminalOperator):
    def __init__(self, operator_id: str, reducer_func: Callable):
        super().__init__(operator_id)
        self.reducer_func = reducer_func

    def process(self, *data: Iterable[Any]) -> Any:
        return reduce(self.reducer_func, data)
