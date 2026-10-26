import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

from flakyreport.parser import parse_file

RUNS = Path(__file__).resolve().parent.parent / "runs"


def test_real_file_gives_one_result_per_testcase():
    results = parse_file(RUNS / "run-001.xml")
    assert len(results) == 18


def test_failure_element_is_a_fail():
    results = dict(parse_file(RUNS / "run-001.xml"))
    assert results[("tests.test_auth", "test_session_expires")] == "fail"


def test_no_child_element_is_a_pass():
    results = dict(parse_file(RUNS / "run-001.xml"))
    assert results[("tests.test_auth", "test_login_valid_credentials")] == "pass"


def test_truncated_file_raises_parse_error():
    with pytest.raises(ET.ParseError):
        parse_file(RUNS / "run-009.xml")


def test_empty_file_raises_parse_error(tmp_path):
    empty = tmp_path / "empty.xml"
    empty.write_text("")
    with pytest.raises(ET.ParseError):
        parse_file(empty)
