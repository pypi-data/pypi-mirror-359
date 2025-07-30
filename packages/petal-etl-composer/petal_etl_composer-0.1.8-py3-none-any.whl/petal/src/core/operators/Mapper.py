from typing import Any

from petal.src.core.operators.NonTerminalOperator import NonTerminalOperator


class Mapper(NonTerminalOperator):
    def __init__(self, operator_id: str):
        super().__init__(operator_id)

    def process(self, data: Any) -> Any:
        pass
