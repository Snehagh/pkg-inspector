"""Allow ``python -m pkg_inspector``."""

from .cli import main

if __name__ == "__main__":
    raise SystemExit(main())
