import re
from petal.src.core.operators.Mapper import Mapper


class RegexMapper(Mapper):
    def __init__(self, operator_id: str, pattern: str):
        super().__init__(operator_id, lambda x: self.pattern.findall(x)[0])
        self.pattern = re.compile(pattern)
