from typing import Iterable, Any

from petal.src.core.operators.Sink import Sink


class Writer(Sink):
    def __init__(self, operator_id: str):
        super().__init__(operator_id)

    def process(self, data: Iterable[Any]) -> None:
        pass
