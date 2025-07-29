from core import Pipeline
from plugins.EmptySource import EmptySource

from src.plugins.NoOpSink import NoOpSink


def main():
    with Pipeline("01_noop") as dag:
        source = EmptySource("empty_source")
        sink = NoOpSink("no_op_sink")

        source >> sink

    dag.run()


if __name__ == '__main__':
    main()
