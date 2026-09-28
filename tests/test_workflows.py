"""Workflows pin third-party actions and declare permissions."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from validation import workflows
from validation.common import REPO_ROOT

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


RELEASE = ".github/workflows/release.yml"


def _workflow(relative: str) -> dict[str, Any]:
    data = yaml.safe_load((REPO_ROOT / relative).read_text(encoding="utf-8"))
    assert isinstance(data, dict)
    # YAML 1.1 reads the bare key 'on' as True.
    data["on"] = data.pop(True, data.get("on"))
    return data


def test_release_publishes_only_after_every_validation_check() -> None:
    release = _workflow(RELEASE)
    assert release["on"] == {"push": {"tags": ["v*"]}}
    assert release["permissions"] == {"contents": "read"}
    jobs = release["jobs"]
    assert jobs["validate"]["uses"] == "./.github/workflows/validate.yml"
    publish = jobs["publish"]
    assert publish["needs"] == "validate"
    assert publish["permissions"] == {"contents": "write"}
    scripts = "\n".join(step.get("run", "") for step in publish["steps"])
    assert 'validate.py versions --ref "$GITHUB_REF"' in scripts
    assert "release_notes.py" in scripts
    assert "gh release create" in scripts and "--verify-tag" in scripts
    assert "SHA256SUMS" in scripts


def test_validate_is_reusable_and_leaves_tags_to_release() -> None:
    triggers = _workflow(".github/workflows/validate.yml")["on"]
    assert "workflow_call" in triggers
    assert "tags" not in triggers["push"]


def test_release_actions_must_be_pinned(repo: Path) -> None:
    replace_text(
        repo,
        RELEASE,
        "astral-sh/setup-uv@c18668ad3cf93ea998bef934396af7bb5c839dc7",
        "astral-sh/setup-uv@v10",
    )
    assert any("release.yml" in e and "setup-uv@v10" in e for e in errors(workflows.check(repo)))
