"""Workflows pin third-party actions and declare permissions."""

from __future__ import annotations

from pathlib import Path

from validation import workflows

from .conftest import errors, replace_text

WORKFLOW = ".github/workflows/validate.yml"


def test_unpinned_action_is_rejected(repo: Path) -> None:
    replace_text(
        repo,
        WORKFLOW,
        "actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1",
        "actions/checkout@v7",
    )
    assert any("actions/checkout@v7" in e for e in errors(workflows.check(repo)))


def test_permissions_are_required(repo: Path) -> None:
    replace_text(repo, WORKFLOW, "permissions:\n  contents: read\n", "")
    assert any("permissions" in e for e in errors(workflows.check(repo)))
