import pytest

from flakyreport.analysis import classify, ranked

SESSION = ("tests.test_auth", "test_session_expires")
LOGIN = ("tests.test_auth", "test_login_valid")
CONCURRENT = ("tests.test_report", "test_concurrent")
DICOM = ("tests.test_export", "test_export_dicom")


def test_mixed_pass_and_fail_is_flaky_with_correct_counts():
    stats = classify([[(SESSION, "fail")], [(SESSION, "pass")], [(SESSION, "pass")]])[SESSION]
    assert (stats.passes, stats.fails, stats.category) == (2, 1, "flaky")
    assert stats.fail_rate == pytest.approx(1 / 3)


def test_all_fail_is_broken_not_flaky():
    stats = classify([[(CONCURRENT, "fail")], [(CONCURRENT, "fail")]])[CONCURRENT]
    assert (stats.passes, stats.fails, stats.category) == (0, 2, "broken")
    assert stats.fail_rate == pytest.approx(1.0)


def test_all_pass_is_stable():
    stats = classify([[(LOGIN, "pass")], [(LOGIN, "pass")]])[LOGIN]
    assert (stats.passes, stats.fails, stats.category) == (2, 0, "stable")
    assert stats.fail_rate == pytest.approx(0.0)


def test_test_missing_from_some_runs_counts_only_runs_it_appeared_in():
    stats = classify([[(DICOM, "fail"), (LOGIN, "pass")], [(LOGIN, "pass")], [(DICOM, "pass"), (LOGIN, "pass")]])[DICOM]
    assert (stats.passes, stats.fails) == (1, 1)
    assert stats.fail_rate == pytest.approx(0.5)


def test_same_name_in_different_classnames_are_different_tests():
    a = ("tests.test_a", "test_save")
    b = ("tests.test_b", "test_save")
    result = classify([[(a, "pass"), (b, "fail")], [(a, "pass"), (b, "fail")]])
    assert result[a].category == "stable"
    assert result[b].category == "broken"


def test_skips_are_counted_but_not_as_pass_or_fail():
    stats = classify([[(DICOM, "skip")], [(DICOM, "skip")], [(DICOM, "pass")]])[DICOM]
    assert (stats.passes, stats.fails, stats.skips, stats.category) == (1, 0, 2, "stable")
    assert stats.fail_rate == pytest.approx(0.0)


def test_only_ever_skipped_has_no_fail_rate():
    stats = classify([[(DICOM, "skip")], [(DICOM, "skip")]])[DICOM]
    assert (stats.passes, stats.fails, stats.skips, stats.category) == (0, 0, 2, "skipped")
    assert stats.fail_rate is None


def test_ranked_sorts_by_fail_rate_then_test_id():
    x = ("tests.b", "test_x")
    y = ("tests.a", "test_y")
    z = ("tests.c", "test_z")
    # x and y tie at 50%; z is worse at 2/3. Ties break alphabetically by test_id.
    runs = [
        [(x, "fail"), (y, "fail"), (z, "fail")],
        [(x, "pass"), (y, "pass"), (z, "fail")],
        [(z, "pass")],
    ]
    order = [test_id for test_id, _ in ranked(classify(runs), "flaky")]
    assert order == [z, y, x]


def test_ranked_only_returns_the_requested_category():
    runs = [[(SESSION, "fail"), (CONCURRENT, "fail"), (LOGIN, "pass")], [(SESSION, "pass"), (CONCURRENT, "fail"), (LOGIN, "pass")]]
    assert [t for t, _ in ranked(classify(runs), "broken")] == [CONCURRENT]
