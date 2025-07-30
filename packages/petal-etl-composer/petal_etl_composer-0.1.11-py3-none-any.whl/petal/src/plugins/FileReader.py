from typing import Iterable

from petal.src.logger import logger
from petal.src.core.operators.Reader import Reader


class FileReader(Reader):

    def __init__(self, operator_id: str, file_path: str):
        super().__init__(operator_id)
        self.file_path = file_path

    def process(self) -> Iterable[str]:
        logger.info(f"\t\tFileReader: reading file {self.file_path}.")
        try:
            with open(self.file_path, 'r') as f:
                ctr = 0
                for line in f.readlines():
                    logger.info(f'\t\tFileReader: reading line {ctr}...')
                    yield line
                    ctr += 1
            logger.info("\t\tFileReader: done reading.")
        except FileNotFoundError as e:
            logger.error(f"\t\tFileReader: no such file {self.file_path}")
            raise e
