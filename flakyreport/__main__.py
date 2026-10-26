import argparse
import sys
from pathlib import Path

from flakyreport.analysis import classify, ranked
from flakyreport.parser import load_runs


def format_test_id(test_id):
    classname, name = test_id
    return f"{classname}.{name}"


def print_section(heading, rows):
    print(heading)
    if not rows:
        print("  none")
    for test_id, s in rows:
        print(f"  {s.fail_rate:6.1%}  {s.passes} pass  {s.fails} fail  {s.skips} skip  {format_test_id(test_id)}")
    print()


def main(argv=None):
    parser = argparse.ArgumentParser(prog="flakyreport", description="Report flaky tests from JUnit XML files.")
    parser.add_argument("directory", type=Path, help="directory containing JUnit XML files")
    args = parser.parse_args(argv)

    if not args.directory.is_dir():
        print(f"error: {args.directory} is not a directory", file=sys.stderr)
        return 2

    runs, skipped = load_runs(args.directory)
    for path, reason in skipped:
        print(f"WARNING: skipped {path.name}: {reason}", file=sys.stderr)

    total_files = len(runs) + len(skipped)
    if total_files == 0:
        print(f"error: no .xml files found in {args.directory}", file=sys.stderr)
        return 1
    if not runs:
        print(f"error: no readable .xml files in {args.directory}", file=sys.stderr)
        return 1

    stats = classify(runs)
    counts = {c: sum(1 for s in stats.values() if s.category == c) for c in ("flaky", "broken", "stable", "skipped")}

    files_line = f"Read {len(runs)} of {total_files} files"
    if skipped:
        files_line += f" ({len(skipped)} skipped: {', '.join(p.name for p, _ in skipped)})"
    print(files_line)
    print(f"{len(stats)} tests: {counts['flaky']} flaky, {counts['broken']} broken, "
          f"{counts['stable']} stable, {counts['skipped']} skipped")
    print()
    print_section("Flaky tests (passed in some runs, failed in others), worst first:", ranked(stats, "flaky"))
    print_section("Broken tests (failed in every run they were counted):", ranked(stats, "broken"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
