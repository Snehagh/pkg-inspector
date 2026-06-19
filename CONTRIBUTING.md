# Contributing

Thanks for your interest in pkg-inspector.

## Getting started

```bash
python -m pip install -e ".[dev]"
pytest
ruff check .
```

## Adding a check

Checks live in `src/pkg_inspector/checks.py`. To add one:

1. Write a function `check_<thing>(ctx: ProjectContext) -> CheckResult`.
2. Keep it standard-library only and side-effect free (read, don't write).
3. Register it in the `ALL_CHECKS` tuple.
4. Add a test in `tests/test_checks.py`.

A check should return `PASS`, `WARN`, or `FAIL` with a short, actionable
message. Use a higher `weight` only for things a packager genuinely cannot
proceed without (e.g. licensing).

## Pull requests

- Keep PRs focused and small.
- All tests and `ruff` must pass; CI enforces this.
- Describe the *why*, not just the *what*, in the PR description.

## Code of Conduct

Be respectful and constructive. Assume good faith.
