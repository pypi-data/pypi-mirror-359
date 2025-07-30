from typing import Iterable, Any

from petal.src.plugins.Joiner import Joiner


# Takes in a list of streams and flattens them all into a single output stream
def concatenate_inputs(*args: Iterable[Iterable[Any]]) -> Iterable[Any]:
    for arg in args:
        yield from arg


class StreamJoiner(Joiner):

    def __init__(self, operator_id: str):
        super().__init__(operator_id, concatenate_inputs)
