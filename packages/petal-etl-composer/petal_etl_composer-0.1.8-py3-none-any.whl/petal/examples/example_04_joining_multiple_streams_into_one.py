from petal.src.core.pipeline import Pipeline
from petal.src.plugins.FileReader import FileReader
from petal.src.plugins.FileWriter import FileWriter
from petal.src.plugins.StreamJoiner import StreamJoiner


def main():
    with Pipeline("example_04_joining_multiple_streams_into_one") as dag:
        source_1 = FileReader("source_1", file_path="../data/source_1.txt")
        source_2 = FileReader("source_2", file_path="../data/source_2.txt")
        source_3 = FileReader("source_3", file_path="../data/source_3.txt")

        joiner = StreamJoiner("joiner")

        write_to_file = FileWriter("write_to_file", file_path="../data/all_concatenated.txt")

        source_1 >> joiner
        source_2 >> joiner
        source_3 >> joiner
        joiner >> write_to_file

    dag.run()


if __name__ == '__main__':
    main()
