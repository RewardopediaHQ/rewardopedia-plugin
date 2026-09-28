"""Manifest, changelog and tag versions must agree."""

from __future__ import annotations

from pathlib import Path

import pytest

from validation import versions

from .conftest import edit_json, errors, replace_text

RELEASED = "## [Unreleased]\n\n## [0.1.0] - 2026-10-01\n\n### Added\n\n- Initial release.\n"


def set_version(root: Path, version: str) -> None:
    for manifest in ("plugin.json", ".claude-plugin/plugin.json"):
        edit_json(root, manifest, lambda d: d.update(version=version))


def release_changelog(root: Path) -> None:
    replace_text(root, "CHANGELOG.md", "## [Unreleased]\n", RELEASED)


def test_manifest_versions_must_match(repo: Path) -> None:
    edit_json(repo, ".claude-plugin/plugin.json", lambda d: d.update(version="0.2.0-dev"))
    assert any("versions differ" in e for e in errors(versions.check(repo, ref="")))


def test_marketplace_entry_version_must_match(repo: Path) -> None:
    edit_json(
        repo,
        ".claude-plugin/marketplace.json",
        lambda d: d["plugins"][0].update(version="9.9.9"),
    )
    assert any("versions differ" in e for e in errors(versions.check(repo, ref="")))


def test_version_must_be_semver(repo: Path) -> None:
    set_version(repo, "v0.1")
    assert any("Semantic Versioning" in e for e in errors(versions.check(repo, ref="")))


def test_untagged_release_version_needs_changelog_section(repo: Path) -> None:
    set_version(repo, "0.1.0")
    assert any("needs a dated changelog" in e for e in errors(versions.check(repo, ref="")))


def test_release_preparation_passes_with_dated_section(repo: Path) -> None:
    set_version(repo, "0.1.0")
    release_changelog(repo)
    assert errors(versions.check(repo, ref="refs/heads/main")) == []


def test_tag_must_match_manifest_version(repo: Path) -> None:
    set_version(repo, "0.1.0")
    release_changelog(repo)
    assert any("does not match" in e for e in errors(versions.check(repo, ref="refs/tags/v0.2.0")))


def test_matching_tag_passes(repo: Path) -> None:
    set_version(repo, "0.1.0")
    release_changelog(repo)
    assert errors(versions.check(repo, ref="refs/tags/v0.1.0")) == []


def test_dev_version_cannot_be_tagged(repo: Path) -> None:
    found = errors(versions.check(repo, ref="refs/tags/v0.1.0-dev"))
    assert any("cannot tag pre-release" in e for e in found)
    assert any("missing '## [0.1.0-dev]" in e for e in found)


def test_dev_version_after_release_must_move_forward(repo: Path) -> None:
    release_changelog(repo)
    assert any("already released" in e for e in errors(versions.check(repo, ref="")))


def test_other_prereleases_are_rejected(repo: Path) -> None:
    set_version(repo, "0.1.0-rc.1")
    assert any("X.Y.Z-dev" in e for e in errors(versions.check(repo, ref="")))


def test_changelog_needs_unreleased_section(repo: Path) -> None:
    replace_text(repo, "CHANGELOG.md", "## [Unreleased]", "## Upcoming")
    assert any("[Unreleased]" in e for e in errors(versions.check(repo, ref="")))


def test_release_headings_need_dates(repo: Path) -> None:
    replace_text(repo, "CHANGELOG.md", "## [Unreleased]\n", "## [Unreleased]\n\n## [0.0.1]\n")
    assert any("needs ' - YYYY-MM-DD'" in e for e in errors(versions.check(repo, ref="")))


def test_github_ref_environment_is_used(repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GITHUB_REF", "refs/tags/v0.1.0-dev")
    assert any("cannot tag pre-release" in e for e in errors(versions.check(repo)))
