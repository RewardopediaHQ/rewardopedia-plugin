"""Cross-file consistency: identity, endpoint, tools, scopes, README and synthetic examples."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from validation import content

from .conftest import edit_json, errors, replace_text, write_json, write_text


def test_endpoint_must_be_canonical(repo: Path) -> None:
    edit_json(
        repo,
        ".mcp.json",
        lambda d: d["mcpServers"]["rewardopedia"].update(url="https://mcp.example.com/mcp"),
    )
    assert any("server url must be" in e for e in errors(content.check_endpoints(repo)))


def test_embedded_headers_are_rejected(repo: Path) -> None:
    edit_json(
        repo,
        "mcp.json",
        lambda d: d["mcpServers"]["rewardopedia"].update(headers={"X-Key": "value"}),
    )
    assert any("no headers" in e for e in errors(content.check_endpoints(repo)))


def test_exactly_one_server(repo: Path) -> None:
    edit_json(
        repo,
        "mcp.json",
        lambda d: d["mcpServers"].update(
            other={"type": "streamable-http", "url": "https://other.example/mcp"}
        ),
    )
    assert any("exactly one server" in e for e in errors(content.check_endpoints(repo)))


def test_identity_must_match_across_manifests(repo: Path) -> None:
    def change(data: dict[str, Any]) -> None:
        data["name"] = "other"
        data["license"] = "Apache-2.0"
        data["description"] = "Different"

    edit_json(repo, ".claude-plugin/plugin.json", change)
    found = errors(content.check_identity(repo))
    assert any("name must be" in e for e in found)
    assert any("license must be" in e for e in found)
    assert any("description differs" in e for e in found)


def test_all_eleven_tools_are_documented(repo: Path) -> None:
    replace_text(repo, content.TOOLS_DOC, "### `get_card_fees`", "### get card fees")
    assert any("tool headings" in e for e in errors(content.check_tools_doc(repo)))


def test_example_schema_tool_enum_matches(repo: Path) -> None:
    edit_json(
        repo,
        "schemas/example.schema.json",
        lambda d: d["$defs"]["tool"]["enum"].remove("forget_my_context"),
    )
    assert any("tool enum" in e for e in errors(content.check_tools_doc(repo)))


README = (
    "# Rewardopedia plugin\n\n"
    "> **NOT YET LIVE.** The server at `https://mcp.rewardopedia.com/mcp` has not launched.\n\n"
    "Scopes: `cards:read`, `context:read` and `context:write`.\n\n"
    "Read the [privacy guide](docs/privacy-and-memory.md) first, then a\n"
    "[setup guide](docs/clients/claude.md).\n"
)
LIVE_README = README.replace(
    "> **NOT YET LIVE.** The server at `https://mcp.rewardopedia.com/mcp` has not launched.",
    "The server is at `https://mcp.rewardopedia.com/mcp`.",
)


@pytest.fixture
def pre_launch(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(content, "SERVICE_LIVE", False)


@pytest.mark.usefixtures("pre_launch")
def test_synthetic_readme_passes(repo: Path) -> None:
    write_text(repo, "README.md", README)
    assert errors(content.check_readme(repo)) == []


@pytest.mark.usefixtures("pre_launch")
def test_readme_needs_banner_scopes_and_privacy_first(repo: Path) -> None:
    text = README.replace("NOT YET LIVE", "Coming soon").replace("`context:write`", "context-write")
    write_text(repo, "README.md", "[Claude](docs/clients/claude.md)\n\n" + text)
    found = errors(content.check_readme(repo))
    assert any("NOT YET LIVE" in e for e in found)
    assert any("context:write" in e for e in found)
    assert any("privacy guide before" in e for e in found)


def test_live_readme_must_drop_the_banner(repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(content, "SERVICE_LIVE", True)
    write_text(repo, "README.md", LIVE_README)
    assert errors(content.check_readme(repo)) == []
    write_text(repo, "README.md", README)
    assert any(
        "remove the 'NOT YET LIVE' banner once live" in e
        for e in errors(content.check_readme(repo))
    )


@pytest.mark.usefixtures("pre_launch")
def test_readme_must_name_the_endpoint(repo: Path) -> None:
    write_text(repo, "README.md", README.replace("https://mcp.rewardopedia.com/mcp", "the server"))
    assert any("must name the endpoint" in e for e in errors(content.check_readme(repo)))


GUIDE = "docs/clients/chatgpt.md"


def test_repository_endpoint_references_are_canonical(repo: Path) -> None:
    assert errors(content.check_endpoint_references(repo)) == []


@pytest.mark.parametrize(
    "url",
    [
        "https://mcp.rewardopedia.com/sse",
        "https://mcp.rewardopedia.com/mcp/",
        "http://mcp.rewardopedia.com/mcp",
    ],
)
def test_guide_endpoint_must_be_canonical(repo: Path, url: str) -> None:
    text = (repo / GUIDE).read_text(encoding="utf-8")
    assert "`https://mcp.rewardopedia.com/mcp`." in text
    write_text(repo, GUIDE, text.replace("`https://mcp.rewardopedia.com/mcp`.", f"`{url}`.", 1))
    assert any(url in e for e in errors(content.check_endpoint_references(repo)))


def test_guide_cannot_point_users_at_another_host(repo: Path) -> None:
    with (repo / GUIDE).open("a", encoding="utf-8") as handle:
        handle.write("\nOr enter `https://connector.example/mcp`.\n")
    assert any("connector.example" in e for e in errors(content.check_endpoint_references(repo)))


def test_lookalike_hosts_are_rejected_anywhere(repo: Path) -> None:
    with (repo / "docs/sources.md").open("a", encoding="utf-8") as handle:
        handle.write("\nSee [setup](https://mcp.rewardopedia.co/mcp).\n")
    edit_json(repo, "plugin.json", lambda d: d.update(homepage="https://rewardopedia-mcp.com"))
    found = errors(content.check_endpoint_references(repo))
    assert any(
        "docs/sources.md" in e and "lookalike" in e and "rewardopedia.co" in e for e in found
    )
    assert any("plugin.json" in e and "rewardopedia-mcp.com" in e for e in found)


def test_every_client_guide_gives_the_endpoint(repo: Path) -> None:
    write_text(repo, "docs/clients/perplexity.md", "# Perplexity\n\nNo endpoint here.\n")
    assert any(
        "Perplexity guide must give the endpoint" in e
        for e in errors(content.check_endpoint_references(repo))
    )


EXAMPLE = "examples/synthetic-test.json"


def example(steps: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "synthetic": True,
        "title": "Test",
        "notice": "Synthetic and illustrative.",
        "locale": "en-US",
        "market": "US",
        "demonstrates": ["Testing."],
        "steps": steps,
    }


NOTICE: dict[str, Any] = {"actor": "assistant", "text": "Rewardopedia keeps a request history."}
CALL: dict[str, Any] = {"actor": "tool_call", "tool": "search_cards", "arguments": {}}


def test_examples_must_use_reserved_domains_and_example_cards(repo: Path) -> None:
    result = {
        "candidates": [{"slug": "real-bank-card", "sources": ["https://www.realbank.com/card"]}]
    }
    steps = [
        NOTICE,
        CALL,
        {"actor": "tool_result", "tool": "search_cards", "outcome": "ok", "result": result},
    ]
    write_json(repo, EXAMPLE, example(steps))
    found = errors(content.check_examples_synthetic(repo))
    assert any("reserved domain" in e for e in found)
    assert any("real-bank-card" in e for e in found)


def test_example_wallet_cards_are_synthetic(repo: Path) -> None:
    result = {"wallet": ["example-cash-card", "real-card"]}
    steps = [
        NOTICE,
        CALL,
        {"actor": "tool_result", "tool": "search_cards", "outcome": "ok", "result": result},
    ]
    write_json(repo, EXAMPLE, example(steps))
    found = errors(content.check_examples_synthetic(repo))
    assert any("real-card" in e for e in found)
    assert not any("example-cash-card" in e for e in found)


def test_examples_give_the_notice_before_the_first_call(repo: Path) -> None:
    write_json(repo, EXAMPLE, example([{"actor": "user", "text": "Hi"}, NOTICE, CALL]))
    assert errors(content.check_examples_notice(repo)) == []
    write_json(repo, EXAMPLE, example([{"actor": "user", "text": "Hi"}, CALL, NOTICE]))
    assert any(EXAMPLE in e for e in errors(content.check_examples_notice(repo)))
