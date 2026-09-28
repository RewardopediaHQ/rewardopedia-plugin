"""Fixtures: an isolated copy of the repository that tests can mutate."""

from __future__ import annotations

import json
import shutil
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest

from validation.common import REPO_ROOT, SKIPPED_DIRS, Finding

IGNORED = shutil.ignore_patterns(*SKIPPED_DIRS)


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    """A copy of the repository outside Git (files are discovered by walking)."""
    target = tmp_path / "repo"
    shutil.copytree(REPO_ROOT, target, ignore=IGNORED)
    return target


def read_json(root: Path, relative: str) -> Any:
    return json.loads((root / relative).read_text(encoding="utf-8"))


def write_json(root: Path, relative: str, data: Any) -> None:
    (root / relative).write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


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
