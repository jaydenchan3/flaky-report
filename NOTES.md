# Scratch notes

## Done means
`python -m flakyreport runs/` prints the flaky tests: name, passes, fails, flake rate,
sorted worst first. Exits non-zero (or warns) on unreadable files instead of crashing.

Definition (the core judgment call; write it in the README):
- Flaky = passed at least once AND failed at least once across runs
- Always failing = broken, NOT flaky. Report it separately.
- Test identity = classname + name
- Pass = testcase with no child element; any child element = not a pass

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
- Out of scope: `<skipped>` and `<error>` tags don't appear in the data, so they aren't handled or tested.
- Broken tests with changing error messages may be hiding instability (pagination_boundary and
  concurrent_edit_conflict fail 8/8 with five different messages).
- 1 failure out of 8 is weak evidence; with this few runs, low flake rates should be read with caution.
- Failures sharing the same messages (503, connection refused to localhost:5000, stale element)
  point to environment problems, so grouping by message is a "with more time" item.
