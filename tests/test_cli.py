import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Expected values counted by hand from runs/*.xml (see NOTES.md), not copied from tool output.
EXPECTED_FLAKY_ORDER = [
    "tests.test_viewer.test_priors_appear",  # 5/8
    "tests.test_auth.test_session_expires",  # 3/8
    "tests.test_api.test_rate_limit_backoff",  # 1/8, ties broken by test_id
    "tests.test_report.test_report_requires_signature",  # 1/8
    "tests.test_worklist.test_filter_by_date_range",  # 1/8
]
EXPECTED_BROKEN = [
    "tests.test_report.test_concurrent_edit_conflict",
    "tests.test_worklist.test_pagination_boundary",
]


def run_cli(*args):
    return subprocess.run(
        [sys.executable, "-m", "flakyreport", *args],
        cwd=ROOT, capture_output=True, text=True,
    )


def section(stdout, heading):
    """Return the test names listed under a heading, in printed order."""
    lines = stdout.splitlines()
    start = next(i for i, line in enumerate(lines) if line.startswith(heading)) + 1
    names = []
    for line in lines[start:]:
        if not line.strip():
            break
        names.append(line.split()[-1])
    return names


def test_real_runs_exit_zero_despite_bad_file():
    assert run_cli("runs").returncode == 0


def test_bad_file_warning_names_file_on_stderr_only():
    result = run_cli("runs")
    assert "run-009.xml" in result.stderr
    assert "not valid XML" in result.stderr
    assert "WARNING" not in result.stdout


def test_report_states_partial_data():
    assert "Read 8 of 9 files (1 skipped: run-009.xml)" in run_cli("runs").stdout


def test_summary_counts_match_hand_count():
    assert "19 tests: 5 flaky, 2 broken, 12 stable, 0 skipped" in run_cli("runs").stdout


def test_flaky_list_is_worst_first():
    assert section(run_cli("runs").stdout, "Flaky") == EXPECTED_FLAKY_ORDER


def test_broken_list_has_both_always_failing_tests():
    assert section(run_cli("runs").stdout, "Broken") == EXPECTED_BROKEN


def test_only_bad_files_exits_one(tmp_path):
    (tmp_path / "bad.xml").write_text("")
    result = run_cli(str(tmp_path))
    assert result.returncode == 1
    assert "no readable" in result.stderr


def test_no_xml_files_exits_one(tmp_path):
    result = run_cli(str(tmp_path))
    assert result.returncode == 1
    assert "no .xml files" in result.stderr


def test_missing_directory_is_an_error():
    result = run_cli("no-such-dir")
    assert result.returncode == 2
    assert "not a directory" in result.stderr


def test_valid_xml_with_no_testcases_is_counted_but_warned(tmp_path):
    (tmp_path / "run-a.xml").write_text((ROOT / "runs" / "run-001.xml").read_text())
    (tmp_path / "run-b.xml").write_text("<testsuites></testsuites>")
    result = run_cli(str(tmp_path))
    assert result.returncode == 0
    assert "WARNING: run-b.xml contained no testcases" in result.stderr
    assert "Read 2 of 2 files" in result.stdout
