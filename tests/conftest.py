"""Fixtures: an isolated copy of the repository that tests can mutate.

Tests must set up the state they assert on (versions, changelog, compatibility
rows, README banner) instead of relying on the repository's current lifecycle
state; tests/test_lifecycle.py reruns the suite after simulated maintainer steps.
"""

from __future__ import annotations

import json
import shutil
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest

from validation.common import REPO_ROOT, Finding, repo_files


def copy_repository(source: Path, target: Path) -> Path:
    """Copy the files validation sees in ``source`` (tracked and unignored) to ``target``."""
    for relative in repo_files(source):
        destination = target / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source / relative, destination)
    return target


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    """A copy of the repository outside Git (files are discovered by walking)."""
    return copy_repository(REPO_ROOT, tmp_path / "repo")


def read_json(root: Path, relative: str) -> Any:
    return json.loads((root / relative).read_text(encoding="utf-8"))


def write_json(root: Path, relative: str, data: Any) -> None:
    write_text(root, relative, json.dumps(data, indent=2) + "\n")


def write_text(root: Path, relative: str, text: str) -> None:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def edit_json(root: Path, relative: str, change: Callable[[Any], None]) -> None:
    data = read_json(root, relative)
    change(data)
    write_json(root, relative, data)


def replace_text(root: Path, relative: str, old: str, new: str) -> None:
    path = root / relative
    text = path.read_text(encoding="utf-8")
    assert old in text, f"{old!r} not found in {relative}"
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def errors(findings: list[Finding]) -> list[str]:
    return [f.render() for f in findings if f.severity == "error"]


def warnings(findings: list[Finding]) -> list[str]:
    return [f.render() for f in findings if f.severity == "warning"]
