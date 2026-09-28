"""GitHub Actions hygiene: pinned actions and explicit, minimal permissions."""

from __future__ import annotations

import re
import shutil
import subprocess
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import yaml

from .common import Finding, repo_files

CHECK = "workflows"
PINNED = re.compile(r"^[^@\s]+@[0-9a-f]{40}$")


def _uses(node: Any) -> Iterator[str]:
    if isinstance(node, dict):
        for key, value in node.items():
            if key == "uses" and isinstance(value, str):
                yield value
            else:
                yield from _uses(value)
    elif isinstance(node, list):
        for item in node:
            yield from _uses(item)


def check(root: Path, actionlint: bool = False) -> list[Finding]:
    findings: list[Finding] = []
    workflows = [
        p
        for p in repo_files(root)
        if p.parts[:2] == (".github", "workflows") and p.suffix in {".yml", ".yaml"}
    ]
    if not workflows:
        findings.append(Finding(CHECK, ".github/workflows", "no workflows found"))
    for path in workflows:
        relative = path.as_posix()
        try:
            data = yaml.safe_load((root / path).read_text(encoding="utf-8"))
        except yaml.YAMLError:
            continue  # reported by the schema check
        if not isinstance(data, dict):
            findings.append(Finding(CHECK, relative, "workflow must be a mapping"))
            continue
        if "permissions" not in data:
            findings.append(Finding(CHECK, relative, "set top-level 'permissions' explicitly"))
        for uses in _uses(data):
            if uses.startswith("./") or uses.startswith("docker://"):
                continue
            if not PINNED.match(uses):
                findings.append(
                    Finding(CHECK, relative, f"pin '{uses}' to a full 40-character commit SHA")
                )
    if actionlint:
        binary = shutil.which("actionlint")
        if binary is None:
            findings.append(Finding(CHECK, ".github/workflows", "actionlint is not installed"))
        else:
            result = subprocess.run(
                [binary, *(p.as_posix() for p in workflows)],
                cwd=root,
                capture_output=True,
                text=True,
            )
            if result.returncode != 0:
                for line in (result.stdout + result.stderr).splitlines():
                    if line.strip():
                        findings.append(Finding(CHECK, ".github/workflows", f"actionlint: {line}"))
    return findings
