"""The repository copy used by tests matches what validation sees in a checkout."""

from __future__ import annotations

import subprocess
from pathlib import Path

from .conftest import copy_repository


def test_copy_skips_gitignored_files(tmp_path: Path) -> None:
    source = tmp_path / "source"
    (source / "docs").mkdir(parents=True)
    subprocess.run(["git", "init", "-q", "-b", "main"], cwd=source, check=True)
    (source / ".gitignore").write_text(".env\n.env.*\n", encoding="utf-8")
    (source / "docs/guide.md").write_text("# Guide\n", encoding="utf-8")
    (source / ".env").write_text("LOCAL=1\n", encoding="utf-8")
    (source / ".env.local").write_text("LOCAL=1\n", encoding="utf-8")
    target = copy_repository(source, tmp_path / "copy")
    copied = sorted(p.relative_to(target).as_posix() for p in target.rglob("*") if p.is_file())
    assert copied == [".gitignore", "docs/guide.md"]
