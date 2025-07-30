import re
from petal.src.core.operators.Filter import Filter


class RegexFilter(Filter):
    def __init__(self, operator_id, pattern):
        super().__init__(operator_id, lambda x: self.pattern.search(x))
        self.pattern = re.compile(pattern)
