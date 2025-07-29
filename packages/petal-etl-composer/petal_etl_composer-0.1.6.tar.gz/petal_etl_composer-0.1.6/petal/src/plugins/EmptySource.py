from petal.src.core.operators.Source import Source


class EmptySource(Source):

    def __init__(self, operator_id: str):
        super().__init__(operator_id)

    def process(self) -> None:
        print("EmptySource: no-op")
