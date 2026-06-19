# pkg-inspector

A small, dependency-free Python CLI that assesses how ready a project is to be
**packaged and distributed**. It inspects a project directory and prints a
weighted readiness score with actionable findings.

```text
$ pkg-inspector analyze .
Packaging Readiness Report
==========================

  ✓ pyproject.toml: pyproject.toml found and parses.
  ✓ package metadata: Project name and version are declared.
  ✓ license: License declared and a license file is present.
  ✓ README: README found.
  ✓ tests: A tests directory is present.
  ✓ CI workflow: A CI workflow is configured.
  ✓ dependency pinning: No runtime dependencies declared; pinning is not required.
  ✓ entry points: Declares console entry point(s): pkg-inspector.
  ✓ .gitignore: .gitignore found.
  ✓ version control: Under git version control.

  10 passed, 0 warnings, 0 failed
  Overall score: 100/100

This repository doubles as a packaging study: the same tool is packaged as a
**snap**, a **rock** (OCI image), and a **Debian package**, with the tradeoffs
written up in [PACKAGING.md](PACKAGING.md).

> Documentation here loosely follows the [Diátaxis](https://diataxis.fr/)
> framework: a tutorial to get started, how-to recipes, a reference, and an
> explanation of the design.

## Tutorial — get it running in two minutes

```bash
git clone https://github.com/Snehagh/pkg-inspector
cd pkg-inspector
python -m pip install -e ".[dev]"
pkg-inspector analyze .
```

## How-to

Analyze another project:

```bash
pkg-inspector analyze /path/to/project
```

Get machine-readable output:

```bash
pkg-inspector analyze . --format json
```

Use it as a CI gate (exit non-zero below a threshold):

```bash
pkg-inspector analyze . --min-score 80
```

## Reference

| Command | Description |
| --- | --- |
| `analyze [PATH]` | Analyze a project (default: current directory). |
| `--format {text,json}` | Output format. Default: `text`. |
| `--min-score N` | Exit with code `1` if the score is below `N`. |
| `--version` | Print the version and exit. |

Exit codes: `0` success, `1` score below `--min-score`, `2` usage error.

## Explanation — what it checks and why

Each check maps to something a downstream packager or distribution actually
cares about: a parseable `pyproject.toml` (PEP 621 metadata), **clear
licensing** (distros will not ship software with ambiguous licensing), tests,
CI, **dependency pinning** (a prerequisite for reproducible builds), and
**declared entry points** (what command the package installs). Scores are
weighted — a missing license or `pyproject.toml` costs more than a missing
`.gitignore`.

The tool has **zero runtime dependencies** by design: the fewer dependencies a
tool has, the less painful it is to package across snap, rock and deb.

## Development

```bash
python -m pip install -e ".[dev]"
pytest
ruff check .
```

## License

[MIT](LICENSE)
