"""Command-line interface for pkg-inspector."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import __version__
from .checks import run_checks
from .report import Report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="pkg-inspector",
        description="Assess how ready a project is to be packaged and distributed.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")

    sub = parser.add_subparsers(dest="command", required=True)
    analyze = sub.add_parser("analyze", help="Analyze a project directory.")
    analyze.add_argument(
        "path", nargs="?", default=".", help="Path to the project (default: current directory)."
    )
    analyze.add_argument(
        "--format", choices=("text", "json"), default="text", help="Output format."
    )
    analyze.add_argument(
        "--min-score",
        type=int,
        default=None,
        metavar="N",
        help="Exit non-zero if the score is below N. Useful as a CI gate.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Entry point. Returns a process exit code."""
    try:
        return _run(argv)
    except BrokenPipeError:
        # Downstream closed the pipe (e.g. `pkg-inspector ... | head`). Exit quietly.
        try:
            sys.stdout.close()
        except BrokenPipeError:
            pass
        return 0


def _run(argv: list[str] | None) -> int:
    args = build_parser().parse_args(argv)

    if args.command == "analyze":
        root = Path(args.path)
        if not root.is_dir():
            print(f"error: not a directory: {root}", file=sys.stderr)
            return 2

        report = Report(run_checks(root))
        output = report.to_json() if args.format == "json" else report.to_text()
        print(output)

        if args.min_score is not None and report.score < args.min_score:
            print(
                f"\nscore {report.score} is below the required minimum {args.min_score}",
                file=sys.stderr,
            )
            return 1
        return 0

    return 2  # pragma: no cover - argparse enforces a valid command


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
