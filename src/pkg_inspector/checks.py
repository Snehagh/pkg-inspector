"""Individual packaging-readiness checks.

Each check takes a :class:`ProjectContext` and returns a :class:`CheckResult`.
Checks are intentionally dependency-free (standard library only) so the tool
itself is trivial to package: fewer runtime dependencies means fewer surprises
when it is built into a snap, a rock, or a .deb.
"""

from __future__ import annotations

import tomllib
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path


class Status(str, Enum):
    """Outcome of a single check."""

    PASS = "pass"
    WARN = "warn"
    FAIL = "fail"


@dataclass
class CheckResult:
    """The result of running one check against a project."""

    name: str
    status: Status
    message: str
    weight: int = 1


@dataclass
class ProjectContext:
    """Pre-computed view of a project directory.

    Parsing ``pyproject.toml`` once here keeps the individual checks fast and
    side-effect free, which in turn keeps them easy to unit test.
    """

    root: Path
    pyproject: dict = field(default_factory=dict)
    pyproject_error: str | None = None

    @classmethod
    def load(cls, root: Path) -> "ProjectContext":
        ctx = cls(root=root)
        pp = root / "pyproject.toml"
        if pp.is_file():
            try:
                with pp.open("rb") as fh:
                    ctx.pyproject = tomllib.load(fh)
            except (tomllib.TOMLDecodeError, OSError) as exc:
                ctx.pyproject_error = str(exc)
        return ctx

    def has_any(self, *names: str) -> bool:
        """True if any of the given relative paths exists (file or dir)."""
        return any((self.root / name).exists() for name in names)


# --- individual checks -------------------------------------------------------


def check_pyproject(ctx: ProjectContext) -> CheckResult:
    if ctx.pyproject_error is not None:
        return CheckResult(
            "pyproject.toml",
            Status.FAIL,
            f"pyproject.toml is present but could not be parsed: {ctx.pyproject_error}",
            weight=3,
        )
    if not ctx.pyproject:
        return CheckResult(
            "pyproject.toml",
            Status.FAIL,
            "No pyproject.toml found. Modern Python packaging expects PEP 621 metadata here.",
            weight=3,
        )
    return CheckResult("pyproject.toml", Status.PASS, "pyproject.toml found and parses.", weight=3)


def check_metadata(ctx: ProjectContext) -> CheckResult:
    project = ctx.pyproject.get("project", {})
    missing = [k for k in ("name", "version") if k not in project]
    # Allow dynamic versioning (PEP 621): version may be declared dynamic.
    if "version" in missing and "version" in project.get("dynamic", []):
        missing.remove("version")
    if missing:
        return CheckResult(
            "package metadata",
            Status.WARN,
            f"pyproject.toml [project] is missing: {', '.join(missing)}.",
            weight=2,
        )
    return CheckResult(
        "package metadata", Status.PASS, "Project name and version are declared.", weight=2
    )


def check_license(ctx: ProjectContext) -> CheckResult:
    project = ctx.pyproject.get("project", {})
    declared = bool(project.get("license")) or "license" in project.get("dynamic", [])
    has_file = ctx.has_any("LICENSE", "LICENSE.txt", "LICENSE.md", "COPYING")
    if declared and has_file:
        return CheckResult("license", Status.PASS, "License declared and a license file is present.")
    if declared or has_file:
        return CheckResult(
            "license",
            Status.WARN,
            "License is only half-specified. Declare it in pyproject.toml AND ship a license file.",
        )
    return CheckResult(
        "license",
        Status.FAIL,
        "No license found. Packagers and distros will not redistribute software with unclear licensing.",
        weight=2,
    )


def check_readme(ctx: ProjectContext) -> CheckResult:
    if ctx.has_any("README.md", "README.rst", "README.txt", "README"):
        return CheckResult("README", Status.PASS, "README found.")
    return CheckResult("README", Status.WARN, "No README found. Users and packagers need a starting point.")


def check_tests(ctx: ProjectContext) -> CheckResult:
    if ctx.has_any("tests", "test"):
        return CheckResult("tests", Status.PASS, "A tests directory is present.")
    # A single top-level test file is better than nothing.
    if any(ctx.root.glob("test_*.py")) or any(ctx.root.glob("*_test.py")):
        return CheckResult("tests", Status.WARN, "Found test files but no dedicated tests/ directory.")
    return CheckResult("tests", Status.FAIL, "No tests found.", weight=2)


def check_ci(ctx: ProjectContext) -> CheckResult:
    workflows = ctx.root / ".github" / "workflows"
    if workflows.is_dir() and any(workflows.glob("*.y*ml")):
        return CheckResult("CI workflow", Status.PASS, "A CI workflow is configured.")
    if ctx.has_any(".gitlab-ci.yml", ".circleci", "azure-pipelines.yml", ".woodpecker.yml"):
        return CheckResult("CI workflow", Status.PASS, "A CI configuration is present.")
    return CheckResult("CI workflow", Status.WARN, "No CI workflow detected.")


def check_lockfile(ctx: ProjectContext) -> CheckResult:
    """Reproducibility signal: are dependencies pinned anywhere?"""
    if ctx.has_any("uv.lock", "poetry.lock", "Pipfile.lock", "requirements.txt", "requirements.lock"):
        return CheckResult("dependency pinning", Status.PASS, "Pinned/locked dependencies found.")
    # A project that declares no runtime dependencies has nothing to pin.
    deps = ctx.pyproject.get("project", {}).get("dependencies", None)
    if ctx.pyproject and deps == []:
        return CheckResult(
            "dependency pinning",
            Status.PASS,
            "No runtime dependencies declared; pinning is not required.",
        )
    return CheckResult(
        "dependency pinning",
        Status.WARN,
        "No lockfile or pinned requirements. Reproducible builds become harder without one.",
    )


def check_entry_points(ctx: ProjectContext) -> CheckResult:
    """Packaging-relevant: what command(s) does this install?"""
    scripts = ctx.pyproject.get("project", {}).get("scripts", {})
    if scripts:
        names = ", ".join(scripts.keys())
        return CheckResult("entry points", Status.PASS, f"Declares console entry point(s): {names}.")
    return CheckResult(
        "entry points",
        Status.WARN,
        "No [project.scripts] entry points. CLIs should declare the command they install.",
    )


def check_gitignore(ctx: ProjectContext) -> CheckResult:
    if ctx.has_any(".gitignore"):
        return CheckResult(".gitignore", Status.PASS, ".gitignore found.")
    return CheckResult(".gitignore", Status.WARN, "No .gitignore; build artifacts may leak into the repo.")


def check_vcs(ctx: ProjectContext) -> CheckResult:
    if ctx.has_any(".git"):
        return CheckResult("version control", Status.PASS, "Under git version control.")
    return CheckResult("version control", Status.WARN, "No .git directory detected.")


# Ordered registry. Add new checks here; tests assert this list is non-empty.
ALL_CHECKS = (
    check_pyproject,
    check_metadata,
    check_license,
    check_readme,
    check_tests,
    check_ci,
    check_lockfile,
    check_entry_points,
    check_gitignore,
    check_vcs,
)


def run_checks(root: Path) -> list[CheckResult]:
    """Run every registered check against ``root`` and return the results."""
    ctx = ProjectContext.load(root)
    return [check(ctx) for check in ALL_CHECKS]
