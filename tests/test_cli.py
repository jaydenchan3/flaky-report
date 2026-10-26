import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def run_cli(*args):
    return subprocess.run(
        [sys.executable, "-m", "flakyreport", *args],
        cwd=ROOT, capture_output=True, text=True,
    )


def test_runs_on_real_directory():
    assert run_cli("runs").returncode == 0


def test_missing_directory_is_an_error():
    result = run_cli("no-such-dir")
    assert result.returncode == 2
    assert "not a directory" in result.stderr
