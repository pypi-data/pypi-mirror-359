import re
from core.operators.Mapper import Mapper


class RegexFilter(Mapper):
    def __init__(self, operator_id, pattern):
        super().__init__(operator_id)
        self.pattern = re.compile(pattern)

    def process(self, lines):
        return [line for line in lines if self.pattern.search(line)]
