"""Aggregate check results into a scored, renderable report."""

from __future__ import annotations

import json
from dataclasses import dataclass

from .checks import CheckResult, Status

# How much of a check's weight each status earns toward the score.
_STATUS_CREDIT = {Status.PASS: 1.0, Status.WARN: 0.5, Status.FAIL: 0.0}

_SYMBOLS = {Status.PASS: "\u2713", Status.WARN: "\u26a0", Status.FAIL: "\u2717"}


@dataclass
class Report:
    """A scored collection of check results."""

    results: list[CheckResult]

    @property
    def score(self) -> int:
        """Weighted readiness score from 0 to 100."""
        total_weight = sum(r.weight for r in self.results)
        if total_weight == 0:
            return 0
        earned = sum(_STATUS_CREDIT[r.status] * r.weight for r in self.results)
        return round(100 * earned / total_weight)

    def counts(self) -> dict[str, int]:
        out = {s.value: 0 for s in Status}
        for r in self.results:
            out[r.status.value] += 1
        return out

    def to_text(self) -> str:
        lines = ["Packaging Readiness Report", "=" * 26, ""]
        for r in self.results:
            lines.append(f"  {_SYMBOLS[r.status]} {r.name}: {r.message}")
        lines.append("")
        c = self.counts()
        lines.append(
            f"  {c['pass']} passed, {c['warn']} warnings, {c['fail']} failed"
        )
        lines.append(f"  Overall score: {self.score}/100")
        return "\n".join(lines)

    def to_json(self) -> str:
        payload = {
            "score": self.score,
            "counts": self.counts(),
            "checks": [
                {"name": r.name, "status": r.status.value, "message": r.message, "weight": r.weight}
                for r in self.results
            ],
        }
        return json.dumps(payload, indent=2)
