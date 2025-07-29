from typing import Any

from petal.src.core.operators import Mapper


class IdentityTransformer(Mapper):

    def process(self, data: Any) -> Any:
        print(f'IdentityTransformer: {data}')
        return data
