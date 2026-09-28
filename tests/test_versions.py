"""Manifest, changelog and tag versions must agree.

Every test starts from a fixture state it writes itself (a -dev version and a
known changelog), so the tests pass whatever version the repository is at.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any

import pytest

from validation import versions
from validation.constants import MARKETPLACE

from .conftest import edit_json, errors, replace_text, write_text
from .lifecycle import set_version

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import release_notes

DEV = "0.4.0-dev"
RELEASE = "0.4.0"
HEADER = "# Changelog\n\nIntroduction.\n\n"
UNRELEASED = HEADER + "## [Unreleased]\n\n### Added\n\n- Something new.\n"
RELEASED = (
    HEADER + "## [Unreleased]\n\n"
    f"## [{RELEASE}] - 2026-10-01\n\n### Added\n\n- Initial release.\n\n"
    "## [0.3.0] - 2026-09-01\n\n### Fixed\n\n- An older fix.\n"
)


def _unversioned_entries(marketplace: dict[str, Any]) -> None:
    for entry in marketplace["plugins"]:
        entry.pop("version", None)


@pytest.fixture
def root(repo: Path) -> Path:
    """The repository copy at a known -dev version with an unreleased changelog."""
    set_version(repo, DEV)
    edit_json(repo, MARKETPLACE, _unversioned_entries)
    write_text(repo, "CHANGELOG.md", UNRELEASED)
    return repo


def test_fixture_state_is_valid(root: Path) -> None:
    assert errors(versions.check(root, ref="refs/heads/main")) == []


def test_manifest_versions_must_match(root: Path) -> None:
    edit_json(root, ".claude-plugin/plugin.json", lambda d: d.update(version="0.9.0-dev"))
    assert any("versions differ" in e for e in errors(versions.check(root, ref="")))


def test_marketplace_entry_version_must_match(root: Path) -> None:
    edit_json(root, MARKETPLACE, lambda d: d["plugins"][0].update(version="9.9.9"))
    assert any("versions differ" in e for e in errors(versions.check(root, ref="")))


def test_version_must_be_semver(root: Path) -> None:
    set_version(root, "v0.1")
    assert any("Semantic Versioning" in e for e in errors(versions.check(root, ref="")))


def test_untagged_release_version_needs_changelog_section(root: Path) -> None:
    set_version(root, RELEASE)
    assert any("needs a dated changelog" in e for e in errors(versions.check(root, ref="")))


def test_release_preparation_passes_with_dated_section(root: Path) -> None:
    set_version(root, RELEASE)
    write_text(root, "CHANGELOG.md", RELEASED)
    assert errors(versions.check(root, ref="refs/heads/main")) == []


def test_tag_must_match_manifest_version(root: Path) -> None:
    set_version(root, RELEASE)
    write_text(root, "CHANGELOG.md", RELEASED)
    found = errors(versions.check(root, ref="refs/tags/v9.0.0"))
    assert any("does not match" in e for e in found)


def test_matching_tag_passes(root: Path) -> None:
    set_version(root, RELEASE)
    write_text(root, "CHANGELOG.md", RELEASED)
    assert errors(versions.check(root, ref=f"refs/tags/v{RELEASE}")) == []


def test_dev_version_cannot_be_tagged(root: Path) -> None:
    found = errors(versions.check(root, ref=f"refs/tags/v{DEV}"))
    assert any("cannot tag pre-release" in e for e in found)
    assert any(f"missing '## [{DEV}]" in e for e in found)


def test_dev_version_after_release_must_move_forward(root: Path) -> None:
    write_text(root, "CHANGELOG.md", RELEASED)
    assert any("already released" in e for e in errors(versions.check(root, ref="")))


def test_next_dev_version_after_release_passes(root: Path) -> None:
    set_version(root, "0.4.1-dev")
    write_text(root, "CHANGELOG.md", RELEASED)
    assert errors(versions.check(root, ref="refs/heads/main")) == []


def test_other_prereleases_are_rejected(root: Path) -> None:
    set_version(root, "0.4.0-rc.1")
    assert any("X.Y.Z-dev" in e for e in errors(versions.check(root, ref="")))


def test_changelog_needs_unreleased_section(root: Path) -> None:
    replace_text(root, "CHANGELOG.md", "## [Unreleased]", "## Upcoming")
    assert any("[Unreleased]" in e for e in errors(versions.check(root, ref="")))


def test_release_headings_need_dates(root: Path) -> None:
    replace_text(root, "CHANGELOG.md", "## [Unreleased]\n", "## [Unreleased]\n\n## [0.0.1]\n")
    assert any("needs ' - YYYY-MM-DD'" in e for e in errors(versions.check(root, ref="")))


def test_github_ref_environment_is_used(root: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GITHUB_REF", f"refs/tags/v{DEV}")
    assert any("cannot tag pre-release" in e for e in errors(versions.check(root)))


def test_release_notes_are_the_version_section() -> None:
    notes = versions.release_notes(RELEASED, RELEASE)
    assert notes == "### Added\n\n- Initial release.\n"
    assert versions.release_notes(RELEASED, "0.3.0") == "### Fixed\n\n- An older fix.\n"


def test_release_notes_drop_shared_link_definitions() -> None:
    changelog = RELEASED + "\n[0.4.0]: https://github.com/RewardopediaHQ/rewardopedia-plugin\n"
    assert versions.release_notes(changelog, "0.3.0") == "### Fixed\n\n- An older fix.\n"


@pytest.mark.parametrize(
    ("changelog", "message"),
    [
        (UNRELEASED, "no '## [0.4.0] - YYYY-MM-DD' section"),
        (HEADER + "## [Unreleased]\n\n## [0.4.0]\n\n- Undated.\n", "needs ' - YYYY-MM-DD'"),
        (HEADER + "## [Unreleased]\n\n## [0.4.0] - 2026-10-01\n", "no changelog entries"),
    ],
)
def test_release_notes_need_a_dated_nonempty_section(changelog: str, message: str) -> None:
    with pytest.raises(ValueError, match=re.escape(message)):
        versions.release_notes(changelog, RELEASE)


def test_release_notes_script(root: Path, capsys: pytest.CaptureFixture[str]) -> None:
    write_text(root, "CHANGELOG.md", RELEASED)
    assert release_notes.main([RELEASE, "--root", str(root)]) == 0
    assert capsys.readouterr().out == "### Added\n\n- Initial release.\n"
    assert release_notes.main(["9.9.9", "--root", str(root)]) == 1
    assert "no '## [9.9.9]" in capsys.readouterr().err
