import argparse
from petal.examples.example_01_noop import main as noop_pipeline


def main():
    parser = argparse.ArgumentParser(description="Run ETL pipeline")
    parser.add_argument('--run', action='store_true', help='Run default pipeline')
    args = parser.parse_args()

    print(f"Invoked petal with args: {args}")
    if args.run:
        noop_pipeline()
