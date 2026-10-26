import argparse
import sys
from pathlib import Path


def main(argv=None):
    parser = argparse.ArgumentParser(prog="flakyreport", description="Report flaky tests from JUnit XML files.")
    parser.add_argument("directory", type=Path, help="directory containing JUnit XML files")
    args = parser.parse_args(argv)

    if not args.directory.is_dir():
        print(f"error: {args.directory} is not a directory", file=sys.stderr)
        return 2

    return 0


if __name__ == "__main__":
    sys.exit(main())
