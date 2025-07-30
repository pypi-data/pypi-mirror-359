from types import GeneratorType

from petal.src.logger import logger
from petal.src.core.context import PipelineContext
from petal.src.core.utils import is_dag, topological_sort


class Pipeline(PipelineContext):
    def __init__(self, pipeline_name: str):
        super().__init__()
        self.name = pipeline_name

    def validate(self):
        if not is_dag(self.edges):
            raise ValueError("Pipeline contains a cycle")

    def run(self):
        self.validate()

        execution_order = topological_sort(self.edges)
        context = {}

        logger.info(f"Executing Pipeline: '{self.name}'")
        logger.info(f"{execution_order=}")
        logger.info(f"{self.edges=}")

        for op_id in execution_order:
            node = self.nodes[op_id]
            inputs = [context[parent.operator_id] for parent in getattr(node, 'upstream', [])]
            logger.info(f"\tExecuting operator: {op_id} with {inputs=}")
            result = node.process(*inputs)
            # If it's a generator, materialize it for memoization
            if isinstance(result, GeneratorType):
                result = list(result)
            context[op_id] = result
