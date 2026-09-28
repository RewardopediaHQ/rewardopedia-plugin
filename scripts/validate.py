"""Run the package validation checks.

Usage:
    uv run python scripts/validate.py all
    uv run python scripts/validate.py links --external
    uv run python scripts/validate.py secrets --history
    uv run python scripts/validate.py versions --ref refs/tags/v0.1.0

Exit status is 1 when any error is found; warnings never fail the run.
"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Callable
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from validation import compat, content, links, schemas, secrets, versions, workflows
from validation.common import REPO_ROOT, Finding

CHECKS = ("schemas", "versions", "content", "compatibility", "links", "secrets", "workflows")


def run(names: list[str], args: argparse.Namespace, root: Path) -> list[Finding]:
    runners: dict[str, Callable[[], list[Finding]]] = {
        "schemas": lambda: schemas.check(root),
        "versions": lambda: versions.check(root, ref=args.ref),
        "content": lambda: content.check(root),
        "compatibility": lambda: compat.check(root),
        "links": lambda: links.check(root, external=args.external),
        "secrets": lambda: secrets.check(root, history=args.history),
        "workflows": lambda: workflows.check(root, actionlint=args.actionlint),
    }
    findings: list[Finding] = []
    for name in names:
        findings.extend(runners[name]())
    return findings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("check", choices=("all", *CHECKS), help="check to run")
    parser.add_argument("--root", type=Path, default=REPO_ROOT, help="repository root")
    parser.add_argument("--external", action="store_true", help="also request external URLs")
    parser.add_argument("--history", action="store_true", help="also scan Git history")
    parser.add_argument("--actionlint", action="store_true", help="also run actionlint")
    parser.add_argument("--ref", default=None, help="Git ref being built (defaults to $GITHUB_REF)")
    args = parser.parse_args(argv)
    names = list(CHECKS) if args.check == "all" else [args.check]
    findings = run(names, args, args.root.resolve())
    for finding in findings:
        print(finding.render())
    errors = sum(1 for f in findings if f.severity == "error")
    warnings = len(findings) - errors
    print(f"{', '.join(names)}: {errors} error(s), {warnings} warning(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
