from collections.abc import Iterable

from core.operators.Writer import Writer


class FileWriter(Writer):

    def __init__(self, operator_id, file_path: str):
        super().__init__(operator_id)
        self.file_path = file_path

    def process(self, data: Iterable[str]) -> None:
        print(f"FileWriter: writing to file {self.file_path}.")
        with open(self.file_path, 'w') as f:
            ctr = 0
            print(f"FileWriter: writing line {ctr}...")
            f.writelines(data)
        print(f"FileWriter: done writing.")

