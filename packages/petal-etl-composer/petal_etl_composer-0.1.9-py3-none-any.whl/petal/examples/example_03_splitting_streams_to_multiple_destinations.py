from petal.src.core.pipeline import Pipeline
from petal.src.plugins.FileReader import FileReader
from petal.src.plugins.FileWriter import FileWriter
from petal.src.plugins.RegexFilter import RegexFilter
from petal.src.plugins.Splitter import Splitter


def main():
    # Until now, we've used linear DAGs but Petal is able to handle any arbitrary DAG
    # Let's demonstrate a DAG that branches out into multiple prongs
    # There are multiple ways to implement this in Petal, we'll just show one here
    with Pipeline("03_splitting_streams_to_multiple_destinations") as dag:
        # We'll read from the same file as before
        read_logs = FileReader("read_logs", file_path="../data/example_input.txt")
        # This is a Splitter operator
        # It will receive a single input stream and will copy it to N output streams
        splitter = Splitter("split")
        # Under the hood, it uses a deepcopy of the stream - but if you have many output streams
        # and know that the consumers of the streams won't be mutating the data, you can implement
        # a custom Splitter that just propagates the input stream without copying it.
        # That's the beauty of Petal - easy extensibility!

        # To demonstrate the 2 branches of the ETL, we'll apply different transformations to each branch
        # For the first branch, we'll filter for INFO lines just like in example_02
        pattern_filter = RegexFilter("filter_info", pattern="^INFO")
        # Then write it to a file whose name indicates it's filtered
        write_to_file_filtered = FileWriter("write_filtered", file_path="../data/example_output_filtered.txt")

        # The other branch will just be a direct copy of the input file - no transformations applied
        write_to_file_unfiltered = FileWriter("write_unfiltered", file_path="../data/example_output_unfiltered.txt")

        # Here's how we define the DAG:
        # The reader will extract the source data into the Splitter
        read_logs >> splitter

        # And then the Splitter will act like a source itself
        # So we can write two branches of the ETL from the Splitter
        # First branch passes through the filter, then to the filtered file
        splitter >> pattern_filter >> write_to_file_filtered
        # And the second branch just copies directly from the Splitter to the unfiltered file
        splitter >> write_to_file_unfiltered

    dag.run()


if __name__ == '__main__':
    main()
