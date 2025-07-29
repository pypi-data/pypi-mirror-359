from abc import ABC, abstractmethod
from typing import Any
from core.context import get_current_pipeline


class BaseOperator(ABC):
    def __init__(self, operator_id: str):
        self.operator_id = operator_id

        # Register self to current DAG
        pipeline = get_current_pipeline()
        if pipeline:
            pipeline.add_node(self)

    def __rshift__(self, other):
        raise NotImplementedError

    def __lshift__(self, other):
        raise NotImplementedError

    @abstractmethod
    def process(self, *inputs: Any) -> Any:
        pass

