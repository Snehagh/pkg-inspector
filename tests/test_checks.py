"""Tests for individual packaging-readiness checks."""

from pathlib import Path

import pytest

from pkg_inspector.checks import (
    ALL_CHECKS,
    ProjectContext,
    Status,
    check_license,
    check_pyproject,
    check_tests,
    run_checks,
)

FIXTURES = Path(__file__).parent / "fixtures"


def test_registry_is_populated():
    assert len(ALL_CHECKS) >= 5


def test_good_project_mostly_passes():
    results = {r.name: r for r in run_checks(FIXTURES / "good_project")}
    assert results["pyproject.toml"].status is Status.PASS
    assert results["license"].status is Status.PASS
    assert results["tests"].status is Status.PASS


def test_bad_project_fails_core_checks():
    results = {r.name: r for r in run_checks(FIXTURES / "bad_project")}
    assert results["pyproject.toml"].status is Status.FAIL
    assert results["license"].status is Status.FAIL


def test_malformed_pyproject_is_a_failure(tmp_path: Path):
    (tmp_path / "pyproject.toml").write_text("this is = not valid toml [[[")
    ctx = ProjectContext.load(tmp_path)
    result = check_pyproject(ctx)
    assert result.status is Status.FAIL
    assert "could not be parsed" in result.message


def test_dynamic_version_is_accepted(tmp_path: Path):
    (tmp_path / "pyproject.toml").write_text(
        '[project]\nname = "x"\ndynamic = ["version"]\n'
    )
    from pkg_inspector.checks import check_metadata

    ctx = ProjectContext.load(tmp_path)
    assert check_metadata(ctx).status is Status.PASS


def test_half_specified_license_warns(tmp_path: Path):
    # License file present but not declared in pyproject -> WARN, not PASS.
    (tmp_path / "LICENSE").write_text("MIT")
    ctx = ProjectContext.load(tmp_path)
    assert check_license(ctx).status is Status.WARN


def test_loose_test_files_warn(tmp_path: Path):
    (tmp_path / "test_thing.py").write_text("def test_x(): pass")
    ctx = ProjectContext.load(tmp_path)
    assert check_tests(ctx).status is Status.WARN


@pytest.mark.parametrize("check", ALL_CHECKS)
def test_every_check_returns_a_result(check, tmp_path: Path):
    ctx = ProjectContext.load(tmp_path)
    result = check(ctx)
    assert result.name
    assert isinstance(result.status, Status)
    assert result.message
