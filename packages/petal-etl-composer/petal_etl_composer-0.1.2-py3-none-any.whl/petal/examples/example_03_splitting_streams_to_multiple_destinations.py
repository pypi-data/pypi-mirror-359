from core.pipeline import Pipeline
from plugins.FileReader import FileReader
from plugins.FileWriter import FileWriter
from plugins.RegexFilter import RegexFilter
from plugins.Splitter import Splitter


def main():
    with Pipeline("03_splitting_streams_to_multiple_destinations") as dag:
        read_logs = FileReader("read_logs", file_path="../data/example_input.txt")
        splitter = Splitter("split")
        pattern_filter = RegexFilter("filter_info", pattern="^INFO")
        write_to_file_filtered = FileWriter("write_filtered", file_path="../data/example_output_filtered.txt")
        write_to_file_unfiltered = FileWriter("write_unfiltered", file_path="../data/example_output_unfiltered.txt")

        read_logs >> splitter
        splitter >> pattern_filter >> write_to_file_filtered
        splitter >> write_to_file_unfiltered

    dag.run()


if __name__ == '__main__':
    main()
