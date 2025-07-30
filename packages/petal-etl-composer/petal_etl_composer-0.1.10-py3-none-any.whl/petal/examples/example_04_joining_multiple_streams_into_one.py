from petal.src.core.pipeline import Pipeline
from petal.src.plugins.FileReader import FileReader
from petal.src.plugins.FileWriter import FileWriter
from petal.src.plugins.StreamJoiner import StreamJoiner


def main():
    # In example_03 we split streams up - now we want the ability to join streams together as well
    # However, joining streams is not trivial - we need to make decisions on how the data is combined
    with Pipeline("example_04_joining_multiple_streams_into_one") as dag:
        # Let's start with 3 distinct sources
        source_1 = FileReader("source_1", file_path="../data/source_1.txt")
        source_2 = FileReader("source_2", file_path="../data/source_2.txt")
        source_3 = FileReader("source_3", file_path="../data/source_3.txt")

        # This is a subclass of the Joiner operator
        # A generic regular Joiner accepts two inputs - the operator name and a reducer function
        # To implement a StreamJoiner, we can subclass the Joiner and define its reducer function
        # In this case, the reducer function concatenates the data from all the streams
        joiner = StreamJoiner("joiner")

        # As always, we need a Sink
        write_to_file = FileWriter("write_to_file", file_path="../data/all_concatenated.txt")

        # We read all the Sources into the Joiner
        source_1 >> joiner
        source_2 >> joiner
        source_3 >> joiner

        # Then route the Joiner to the Sink. As the data passes through, it's `process()` method
        # will execute the reducer function on the inputs and reduce them to a single output stream.
        joiner >> write_to_file

    dag.run()


if __name__ == '__main__':
    main()
