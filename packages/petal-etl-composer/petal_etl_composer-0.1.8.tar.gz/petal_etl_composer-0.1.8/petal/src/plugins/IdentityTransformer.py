from typing import Any

from petal.src.logger import logger
from petal.src.core.operators import Mapper


class IdentityTransformer(Mapper):

    def process(self, data: Any) -> Any:
        logger.info(f'IdentityTransformer: {data}')
        return data
