"""End-to-end tests for the CLI surface."""

from pathlib import Path

import pytest

from pkg_inspector.cli import main

FIXTURES = Path(__file__).parent / "fixtures"


def test_analyze_good_project_exits_zero(capsys):
    code = main(["analyze", str(FIXTURES / "good_project")])
    out = capsys.readouterr().out
    assert code == 0
    assert "Packaging Readiness Report" in out
    assert "Overall score" in out


def test_json_format(capsys):
    code = main(["analyze", str(FIXTURES / "good_project"), "--format", "json"])
    out = capsys.readouterr().out
    assert code == 0
    assert '"score"' in out


def test_min_score_gate_fails_bad_project(capsys):
    code = main(["analyze", str(FIXTURES / "bad_project"), "--min-score", "50"])
    assert code == 1


def test_min_score_gate_passes_good_project():
    code = main(["analyze", str(FIXTURES / "good_project"), "--min-score", "50"])
    assert code == 0


def test_nonexistent_path_errors():
    code = main(["analyze", "/no/such/dir/anywhere"])
    assert code == 2


def test_version_flag_exits_cleanly():
    with pytest.raises(SystemExit) as exc:
        main(["--version"])
    assert exc.value.code == 0
