# flakyreport

Reads a directory of JUnit XML files from CI runs and reports which tests can't be trusted:
**flaky** tests (passed in some runs, failed in others) and **broken** tests (failed every run).
Unreadable files are skipped with a warning, and the report says how many files it actually used.

## Running it

Needs Python 3.11+. On Ubuntu/WSL, `python` may not exist outside a venv, so create it with `python3`:

```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m flakyreport runs/
```

Output on the included data:

```
Read 8 of 9 files (1 skipped: run-009.xml)
19 tests: 5 flaky, 2 broken, 12 stable, 0 skipped

Flaky tests (passed in some runs, failed in others), worst first:
   62.5%  3 pass  5 fail  0 skip  tests.test_viewer.test_priors_appear
   37.5%  5 pass  3 fail  0 skip  tests.test_auth.test_session_expires
   12.5%  7 pass  1 fail  0 skip  tests.test_api.test_rate_limit_backoff
   12.5%  7 pass  1 fail  0 skip  tests.test_report.test_report_requires_signature
   12.5%  7 pass  1 fail  0 skip  tests.test_worklist.test_filter_by_date_range

Broken tests (failed in every run they were counted):
  100.0%  0 pass  8 fail  0 skip  tests.test_report.test_concurrent_edit_conflict
  100.0%  0 pass  8 fail  0 skip  tests.test_worklist.test_pagination_boundary
```

Warnings go to stderr, e.g. `WARNING: skipped run-009.xml: not valid XML (no element found: line 7, column 0)`.

Exit codes: `0` report produced (bad files skipped with a warning), `1` no readable `.xml` files,
`2` bad usage or the directory doesn't exist. Finding flaky tests does **not** fail the command;
it's a report, not a CI gate.

## Definitions

These are the judgment calls the report rests on:

- **Test identity** = `(classname, name)`. Kept as a tuple rather than a joined string, because
  classnames contain dots and a joined string can be ambiguous.
- **Outcome** follows JUnit: a `<failure>` or `<error>` child is a fail, `<skipped>` is a skip,
  anything else is a pass. So a passing test that writes `<system-out>` is not counted as a failure,
  which would otherwise produce a false flaky report.
- **Flaky** = at least one pass and at least one fail. **Broken** = fails, no passes. Broken is
  reported separately: a test that always fails isn't flaky, it's broken.
- **Skips** are counted and shown, but are not a pass or a fail.
- **Fail rate** = fails / (passes + fails), using only the runs a test appeared in. Tests are added
  and removed over time (`test_export_dicom` disappears after run 4, `test_zoom_persists` appears in
  run 5), so a fixed denominator would be wrong.
- **Worst first** = highest fail rate, ties broken by test name so the order is stable.
- **Malformed files** (like the truncated `run-009.xml`) are skipped whole, never partially counted.

## Running the tests

```
python -m pytest
```

## What's tested

I tested three layers, each with its own job:

- **Parser** (`tests/test_parser.py`): does one XML file turn into the right outcomes? These run
  against the real files: run-001 for passes, failures and the testcase count, run-009 for the
  truncated file. The data has no `<system-out>` or `<skipped>`, so those two get small inline XML
  snippets, because getting them wrong is how a passing test turns into a false flaky.
- **Classifier** (`tests/test_analysis.py`): given outcomes from several runs, is each test labelled
  correctly, with the right counts, fail rate and order? Small hand-built inputs keep each rule
  isolated: mixed results, all fails, all passes, a test missing from some runs, two tests sharing a
  name in different classes, skips, and ties in the sort.
- **End to end** (`tests/test_cli.py`): does the real command on `runs/` print the right report? It
  checks the exit code, the warning for run-009 on stderr, the "Read 8 of 9 files" line, the summary
  counts, and the exact order of both lists. It also covers an empty folder, a folder of only bad
  files, a file with no testcases, and a missing directory.

**The expected values came from the XML, not from the code.** I counted the outcomes by hand and
cross-checked with `grep` before the end-to-end test existed. Tests copied from a tool's output pass
by construction, even when the tool is wrong.

That mattered once. My hand count said 9 tests passed in every run. The parser test said run-001
has 18 testcases, and the numbers didn't add up. Recounting showed there are 10. The tool was right
and my count was wrong, and the test only caught it because the two were written independently.

**I checked the tests can fail.** At each step I broke the code on purpose and confirmed the right
test went red before restoring it:

1. Parser calls every testcase a pass → the failure test fails.
2. The old "any child element is a failure" rule → the `<system-out>` and `<skipped>` tests fail.
3. Any failure counts as flaky → the broken-not-flaky test fails. Removing the tie-break → the
   ordering test fails. (I built that test so insertion order is the reverse of the expected order,
   so it can't pass by accident.)
4. The loader lets the parse error through → 7 end-to-end tests fail.

## What I didn't do

I stopped at the scope that answers "which tests can't be trusted" and cut the rest. Known gaps:

**Untested or partly tested**
- The "could not read" path (`OSError`) has no test. Faking an unreadable file under WSL wasn't
  reliable enough to be worth the time.
- `load_runs` is only covered by the end-to-end tests, not by unit tests of its own.
- `<skipped>`, `<error>` and a bare `<testsuite>` root follow the JUnit spec, but the data contains
  none of them. Skipped has one inline test, error shares the failure branch, and the bare root
  isn't tested at all.

**Not handled**
- If the same test appears twice in one run (retries, parametrize collisions), it's counted twice.
- A `<testcase>` with no `classname` gets the ID `(None, name)`.

**Cut on purpose**
- Correlating failures with commits. The XML has no commit information, so there was nothing to
  correlate.
- Grouping by failure message, durations, trends over time, HTML output.

**Limits of the report itself**
- Eight runs is not much evidence. A test that failed once (12.5%) may be flaky or may have been
  unlucky, and a test with only one or two counted runs (watch the skip column) says even less.
- "Broken" may be hiding instability. Both broken tests fail 8 out of 8 times, but with five
  different errors (timeout, 503, connection refused, stale element, assertion). One real bug would
  usually fail the same way every time.
- "Worst first" sorts by highest fail rate. You could argue a test near 50% is the least
  predictable, and a test at 90% is closer to broken.

## With more time

- **Group failures by message.** The same few errors (503, connection refused to `localhost:5000`,
  stale element) recur across many tests, which points to environment problems rather than many
  separate flaky tests.
- **`--strict` flag** that exits 1 when any file is skipped, for anyone who wants bad CI artifacts to
  fail loudly instead of being warned about.
- **`--fail-on-flaky`** (or a threshold) so the tool can act as a CI gate, plus a minimum-runs
  threshold so low-evidence tests are flagged rather than ranked alongside well-sampled ones.
