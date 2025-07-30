from petal.src.core.pipeline import Pipeline
from petal.src.plugins.FileReader import FileReader
from petal.src.plugins.FileWriter import FileWriter
from petal.src.plugins.RegexFilter import RegexFilter


def main():
    # Now let's look at a non-trivial case
    # We will implement 1 step from each of the ETL (Extract, Transform, Load)
    with Pipeline("02_copy_file_to_file") as dag:

        # Extract the data from a file - in this case, INFO and WARN logs
        read_logs = FileReader("read_logs", file_path="../data/example_input.txt")
        # Transform the data - filter it to only match lines that start with INFO
        pattern_filter = RegexFilter("filter_info", pattern="^INFO")
        # Load the data into a destination file
        write_to_file = FileWriter("write_file", file_path="../data/example_output.txt")

        # Specify the order of the ETL
        read_logs >> pattern_filter >> write_to_file

    dag.run()


if __name__ == '__main__':
    main()
