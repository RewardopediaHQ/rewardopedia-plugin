"""The command-line entry point reports findings through its exit status."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import validate

from .conftest import edit_json


def test_clean_repository_exits_zero(repo: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert validate.main(["all", "--root", str(repo), "--ref", "refs/heads/main"]) == 0
    assert "0 error(s)" in capsys.readouterr().out


def test_errors_exit_one(repo: Path, capsys: pytest.CaptureFixture[str]) -> None:
    edit_json(repo, "plugin.json", lambda d: d.update(version="0.2.0-dev"))
    assert validate.main(["versions", "--root", str(repo), "--ref", ""]) == 1
    assert "versions differ" in capsys.readouterr().out
