_pipeline_context_stack = []


def get_current_pipeline():
    return _pipeline_context_stack[-1] if _pipeline_context_stack else None


"""
DAG Implementation
"""


class PipelineContext:
    def __enter__(self):
        _pipeline_context_stack.append(self)
        self.nodes = {}
        self.edges = set()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        _pipeline_context_stack.pop()

    def add_node(self, node):
        self.nodes[node.operator_id] = node

    def add_edge(self, from_node, to_node):
        self.edges.add((from_node.operator_id, to_node.operator_id))
