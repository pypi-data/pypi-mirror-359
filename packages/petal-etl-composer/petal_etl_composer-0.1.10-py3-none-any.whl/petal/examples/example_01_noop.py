from petal.src.core.pipeline import Pipeline
from petal.src.plugins.EmptySource import EmptySource
from petal.src.plugins.NoOpSink import NoOpSink


def main():
    # Let's start with the most trivial pipeline possible:
    # - a Source that produces nothing
    # - s Sink that does nothing with its input
    # This is just to demonstrate the structure of a Petal pipeline

    # First, we define the pipeline context manager.
    # All the code in the inner block will get scoped to this object, automagically registering itself to the ETL!
    with Pipeline("01_noop") as dag:
        # Inside the Pipeline context, we define operators
        # They can be Petal's built-in operators
        # Or we can extend any of Petal's built-ins to support custom use cases
        source = EmptySource("empty_source")
        sink = NoOpSink("no_op_sink")

        # Once the operators are defined, we compose them into a DAG
        # The >> and << operators signify the direction of flow
        source >> sink
        # (an equivalent statement would have been: sink << source)

    # Finally we execute the pipeline
    dag.run()


if __name__ == '__main__':
    main()
