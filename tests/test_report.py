"""Tests for report scoring and rendering."""

import json

from pkg_inspector.checks import CheckResult, Status
from pkg_inspector.report import Report


def _r(status: Status, weight: int = 1) -> CheckResult:
    return CheckResult("x", status, "msg", weight=weight)


def test_all_pass_is_100():
    report = Report([_r(Status.PASS), _r(Status.PASS)])
    assert report.score == 100


def test_all_fail_is_0():
    report = Report([_r(Status.FAIL), _r(Status.FAIL)])
    assert report.score == 0


def test_warn_is_half_credit():
    report = Report([_r(Status.WARN)])
    assert report.score == 50


def test_weighting_changes_the_score():
    # One heavy failing check should drag the score down more than a light one.
    light_fail = Report([_r(Status.PASS, 1), _r(Status.FAIL, 1)])
    heavy_fail = Report([_r(Status.PASS, 1), _r(Status.FAIL, 3)])
    assert heavy_fail.score < light_fail.score


def test_empty_report_scores_zero():
    assert Report([]).score == 0


def test_json_is_valid_and_complete():
    report = Report([_r(Status.PASS), _r(Status.WARN)])
    payload = json.loads(report.to_json())
    assert payload["score"] == report.score
    assert payload["counts"]["pass"] == 1
    assert payload["counts"]["warn"] == 1
    assert len(payload["checks"]) == 2


def test_text_report_includes_score():
    report = Report([_r(Status.PASS)])
    assert "Overall score: 100/100" in report.to_text()
