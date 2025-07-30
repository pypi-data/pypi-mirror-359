from petal.src.core.operators import Mapper


class IdentityTransformer(Mapper):

    def __init__(self, operator_id: str):
        super().__init__(operator_id)
        self.mapping_func = lambda x: x
