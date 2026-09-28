"""Link checks reject broken internal links and classify external responses."""

from __future__ import annotations

from pathlib import Path

import pytest

from validation import links

from .conftest import errors, replace_text, warnings


def test_broken_relative_link_is_reported(repo: Path) -> None:
    replace_text(repo, "README.md", "(docs/compatibility.md)", "(docs/missing.md)")
    assert any("broken relative link: docs/missing.md" in e for e in errors(links.check(repo)))


def test_missing_anchor_is_reported(repo: Path) -> None:
    replace_text(
        repo,
        "docs/compatibility.md",
        "clients/claude.md#developer-surface-claude-code",
        "clients/claude.md#no-such-heading",
    )
    assert any("missing anchor" in e for e in errors(links.check(repo)))


def test_same_file_anchor_is_checked(repo: Path) -> None:
    with (repo / "README.md").open("a", encoding="utf-8") as handle:
        handle.write("\nSee [below](#nowhere).\n")
    assert any("missing anchor: #nowhere" in e for e in errors(links.check(repo)))


def test_link_escaping_repository_is_reported(repo: Path) -> None:
    with (repo / "README.md").open("a", encoding="utf-8") as handle:
        handle.write("\n[outside](../../etc/passwd)\n")
    assert any("escapes the repository" in e for e in errors(links.check(repo)))


def test_plain_http_is_rejected(repo: Path) -> None:
    with (repo / "README.md").open("a", encoding="utf-8") as handle:
        handle.write("\n[insecure](http://example.org/page)\n")
    assert any("use https" in e for e in errors(links.check(repo)))


def test_links_inside_code_are_ignored(repo: Path) -> None:
    with (repo / "README.md").open("a", encoding="utf-8") as handle:
        handle.write("\n`[not a link](missing.md)`\n\n```\n[also not](missing.md)\n```\n")
    assert errors(links.check(repo)) == []


@pytest.mark.parametrize(
    ("heading", "slug"),
    [
        ("Developer surface: Claude Code", "developer-surface-claude-code"),
        ("`search_cards`", "search_cards"),
        ("Privacy, memory, retention and deletion", "privacy-memory-retention-and-deletion"),
        ("Connect (Pro and Max plans)", "connect-pro-and-max-plans"),
    ],
)
def test_github_slug(heading: str, slug: str) -> None:
    assert links.github_slug(heading) == slug


def test_duplicate_headings_get_suffixes() -> None:
    assert links.anchors("# Try it\n\n## Try it\n") == {"try-it", "try-it-1"}


def _external(url: str) -> dict[str, list[tuple[str, int | None]]]:
    return {url: [("README.md", 1)]}


def test_external_404_is_an_error(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(links, "probe", lambda url: (404, None))
    assert errors(links.check_external(_external("https://docs.invalid-host.test/a")))


def test_external_403_is_a_warning(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(links, "probe", lambda url: (403, None))
    findings = links.check_external(_external("https://blocked.test/a"))
    assert errors(findings) == [] and warnings(findings)


def test_external_connection_failure_is_an_error(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(links, "probe", lambda url: (None, "Name or service not known"))
    assert errors(links.check_external(_external("https://missing.test/a")))


def test_not_yet_live_and_example_hosts_are_skipped(monkeypatch: pytest.MonkeyPatch) -> None:
    def fail(url: str) -> tuple[int | None, str | None]:
        raise AssertionError(f"should not request {url}")

    monkeypatch.setattr(links, "probe", fail)
    urls = {
        **_external("https://mcp.rewardopedia.com/mcp"),
        **_external("https://issuer.example/cards"),
        **_external("https://github.com/RewardopediaHQ/rewardopedia-plugin"),
    }
    assert links.check_external(urls) == []
