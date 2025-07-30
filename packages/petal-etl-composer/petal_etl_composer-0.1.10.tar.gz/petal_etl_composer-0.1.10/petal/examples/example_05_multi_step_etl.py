from petal.src.core.pipeline import Pipeline
from petal.src.plugins.FileReader import FileReader
from petal.src.plugins.RegexFilter import RegexFilter
from petal.src.plugins.Splitter import Splitter
from petal.src.plugins.RegexMapper import RegexMapper
from petal.src.plugins.StreamJoiner import StreamJoiner
from petal.src.plugins.FileWriter import FileWriter
from petal.src.plugins.SqsWriter import MockSqsWriter


def main():
    # We're now ready to compose a complex multi-stage ETL.
    with Pipeline("example_05_multi_step_etl") as dag:
        # Let's start with our Sources...
        log_file = FileReader("log_file", file_path="../data/app_logs.txt")
        events_file = FileReader("events_file", file_path="../data/vm_events.txt")

        # ...then the non-terminal operators...
        event_file_splitter = Splitter("event_file_splitter")
        filter_for_helo_lines = RegexFilter("filter_for_helo_lines", "HELO")
        filter_for_ping_events = RegexFilter("filter_for_ping_events", "PING")
        map_to_ip_addr = RegexMapper("map_to_ip_addr", r"(?:[0-9]{1,3}\.){3}[0-9]{1,3}")
        ping_splitter = Splitter("ping_splitter")
        joiner = StreamJoiner("joiner")

        # ...and finally our Sinks
        write_to_ping_file = FileWriter("write_to_ping_file", file_path="../data/detected_pings.txt")
        write_to_sqs = MockSqsWriter("write_to_sqs", "<sqs_queue_name>", "us-east-1")

        # Now let's piece together this DAG
        log_file >> joiner >> write_to_sqs
        events_file >> event_file_splitter
        event_file_splitter >> filter_for_helo_lines >> map_to_ip_addr >> joiner
        event_file_splitter >> filter_for_ping_events >> ping_splitter
        ping_splitter >> joiner
        ping_splitter >> write_to_ping_file

    dag.run()


if __name__ == '__main__':
    main()
