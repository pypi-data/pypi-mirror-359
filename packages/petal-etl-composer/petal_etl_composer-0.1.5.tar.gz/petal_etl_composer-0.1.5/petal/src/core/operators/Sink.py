from abc import ABC

from core.operators.BaseOperator import BaseOperator


class Sink(BaseOperator, ABC):
    def __init__(self, operator_id: str):
        super().__init__(operator_id)
        self.upstream = []

    def __lshift__(self, other):
        # self << other
        return other.__rshift__(self)
