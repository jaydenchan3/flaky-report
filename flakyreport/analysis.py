from collections import defaultdict
from typing import NamedTuple, Optional


class Stats(NamedTuple):
    passes: int
    fails: int
    skips: int
    category: str  # "flaky" | "broken" | "stable" | "skipped"
    fail_rate: Optional[float]  # fails / (passes + fails); None if only ever skipped


def classify(runs):
    """Combine parse_file() results from many runs into {test_id: Stats}.

    runs is one list of (test_id, outcome) per readable file. A test only counts the
    runs it appears in, and skips are counted separately from passes and fails.
    """
    counts = defaultdict(lambda: {"pass": 0, "fail": 0, "skip": 0})
    for run in runs:
        for test_id, outcome in run:
            counts[test_id][outcome] += 1

    stats = {}
    for test_id, c in counts.items():
        passes, fails, skips = c["pass"], c["fail"], c["skip"]
        if passes and fails:
            category = "flaky"
        elif fails:
            category = "broken"
        elif passes:
            category = "stable"
        else:
            category = "skipped"
        counted = passes + fails
        fail_rate = fails / counted if counted else None
        stats[test_id] = Stats(passes, fails, skips, category, fail_rate)
    return stats


def ranked(stats, category):
    """Return [(test_id, Stats)] in one category, highest fail rate first, ties by test_id."""
    chosen = [(test_id, s) for test_id, s in stats.items() if s.category == category]
    return sorted(chosen, key=lambda item: (-(item[1].fail_rate or 0), item[0]))
