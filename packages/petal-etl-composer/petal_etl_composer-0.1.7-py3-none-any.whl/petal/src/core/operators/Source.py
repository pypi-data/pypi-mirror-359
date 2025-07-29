from abc import ABC

from petal.src.core.operators.BaseOperator import BaseOperator
from petal.src.core.context import get_current_pipeline


class Source(BaseOperator, ABC):
    def __init__(self, operator_id: str):
        super().__init__(operator_id)
        self.downstream = []

    def __rshift__(self, other):
        # self >> other
        self.downstream.append(other)
        other.upstream.append(self)

        pipeline = get_current_pipeline()
        if pipeline:
            pipeline.add_edge(self, other)
        return other
