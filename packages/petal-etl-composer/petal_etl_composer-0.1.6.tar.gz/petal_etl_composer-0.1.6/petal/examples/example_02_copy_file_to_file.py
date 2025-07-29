from petal.src.core.pipeline import Pipeline
from petal.src.plugins.FileReader import FileReader
from petal.src.plugins.FileWriter import FileWriter
from petal.src.plugins.RegexFilter import RegexFilter


def main():
    with Pipeline("02_copy_file_to_file") as dag:
        read_logs = FileReader("read_logs", file_path="../data/example_input.txt")
        pattern_filter = RegexFilter("filter_info", pattern="^INFO")
        write_to_file = FileWriter("write_file", file_path="../data/example_output.txt")

        read_logs >> pattern_filter >> write_to_file

    dag.run()


if __name__ == '__main__':
    main()
