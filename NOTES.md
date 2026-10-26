# Scratch notes

## Done means
`python -m flakyreport runs/` prints the flaky tests: name, passes, fails, fail rate,
sorted worst first. Warns and skips unreadable files (exit 0) instead of crashing.

Definition (the core judgment call; write it in the README):
- Flaky = passed at least once AND failed at least once across runs
- Always failing = broken, NOT flaky. Report it separately.
- Test identity = (classname, name) tuple
- Outcome per JUnit: <failure> or <error> = fail, <skipped> = skip, otherwise pass
  (so <system-out> on a passing test doesn't create a false flaky)
- Skips are not counted as a pass or a fail

## Not doing
- HTML/dashboard output
- Correlating with commits / "failed on the same code" (unless the XML has it)
- Duration or slowness analysis
- Trends over time, config files, packaging

## Riskiest part
Parsing real-world XML variations (root shape, error vs failure, bad files).
So: parser + tests on the real files first.

## Test cases
- ⭐ mixed pass/fail → flaky, with the correct pass/fail counts
- ⭐ all fail → broken, not flaky
- ⭐ malformed file → skipped with a warning, and the other files still get processed
- all pass → stable
- a test missing from some runs → its rate uses only the runs it appeared in
- the same test across files is matched by classname + name
- end to end: running on runs/ gives the hand-counted table (5 flaky, 2 broken)

## README lines (save for later)
- `<skipped>`, `<error>` and `<system-out>` don't appear in the data. They are handled per the JUnit
  spec, with small inline tests for <system-out> (still a pass) and <skipped> (a skip).
- Fail-to-pass: the <system-out> and <skipped> tests failed against the old "any child = fail" rule.
- "Worst first" = highest fail rate. Arguably a test closest to 50% is the least predictable.
- A category resting on only one or two counted runs (see the skips column) is weak evidence.
- Broken tests with changing error messages may be hiding instability (pagination_boundary and
  concurrent_edit_conflict fail 8/8 with five different messages).
- 1 failure out of 8 is weak evidence; with this few runs, low fail rates should be read with caution.
- Failures sharing the same messages (503, connection refused to localhost:5000, stale element)
  point to environment problems, so grouping by message is a "with more time" item.
- Hand count vs tool: my first hand-count table said "the 9 others" stable; cross-checking against the
  parser's 18-testcase count showed it was 10 (12 stable, 19 unique tests total). The hand count was wrong.

## Expected end-to-end (from the XML, runs 1-8)
- 19 tests: 5 flaky, 2 broken, 12 stable, 0 skipped
- Flaky order: priors_appear 5/8, session_expires 3/8, then 12.5%: test_api.test_rate_limit_backoff,
  test_report.test_report_requires_signature, test_worklist.test_filter_by_date_range
- Broken: test_report.test_concurrent_edit_conflict, test_worklist.test_pagination_boundary
- Fail-to-pass (slice 3): letting ParseError escape the loader made 7 end-to-end tests fail
  (crash on run-009 instead of warn-and-skip).
