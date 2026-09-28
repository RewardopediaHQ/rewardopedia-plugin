"""Shared helpers: findings, repository files and JSON loading."""

from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

Severity = Literal["error", "warning"]

REPO_ROOT = Path(__file__).resolve().parent.parent

# Directories never scanned, even when a repository is not a Git checkout.
SKIPPED_DIRS = frozenset(
    {".git", ".venv", "node_modules", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache"}
)


@dataclass(frozen=True)
class Finding:
    """One validation result tied to a file (and optionally a line)."""

    check: str
    path: str
    message: str
    severity: Severity = "error"
    line: int | None = None

    def render(self) -> str:
        location = f"{self.path}:{self.line}" if self.line is not None else self.path
        return f"{self.severity.upper()} [{self.check}] {location}: {self.message}"


def repo_files(root: Path) -> list[Path]:
    """Return tracked and untracked-but-not-ignored files, relative to ``root``.

    Falls back to a directory walk when ``root`` is not a Git work tree, so the
    checks also run on an unpacked archive.
    """
    try:
        output = subprocess.run(
            ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
            cwd=root,
            check=True,
            capture_output=True,
        ).stdout
    except (OSError, subprocess.CalledProcessError):
        files = [
            path.relative_to(root)
            for path in root.rglob("*")
            if path.is_file() and not SKIPPED_DIRS.intersection(path.relative_to(root).parts)
        ]
        return sorted(files)
    names = {name for name in output.decode("utf-8").split("\0") if name}
    return sorted(Path(name) for name in names if (root / name).is_file())


def load_json(root: Path, relative: str, check: str) -> tuple[Any, list[Finding]]:
    """Load a JSON file, returning ``(data, findings)``; data is None on failure."""
    path = root / relative
    if not path.is_file():
        return None, [Finding(check, relative, "file is missing")]
    try:
        return json.loads(path.read_text(encoding="utf-8")), []
    except json.JSONDecodeError as error:
        return None, [Finding(check, relative, f"invalid JSON: {error.msg}", line=error.lineno)]


def read_text(root: Path, relative: str) -> str | None:
    path = root / relative
    if not path.is_file():
        return None
    return path.read_text(encoding="utf-8")
