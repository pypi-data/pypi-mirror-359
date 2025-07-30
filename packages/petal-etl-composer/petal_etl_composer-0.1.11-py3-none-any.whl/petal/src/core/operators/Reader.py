from typing import Iterable, Any

from petal.src.core.operators.Source import Source


class Reader(Source):
    def __init__(self, operator_id: str):
        super().__init__(operator_id)

    def process(self) -> Iterable[Any]:  # or AsyncIterable
        pass
