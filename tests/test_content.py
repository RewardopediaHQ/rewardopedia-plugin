"""Cross-file consistency: identity, endpoint, tools, scopes, README and synthetic examples."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from validation import content

from .conftest import edit_json, errors, replace_text


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


def test_readme_needs_banner_scopes_and_privacy_first(repo: Path) -> None:
    replace_text(repo, "README.md", "NOT YET LIVE", "Coming soon")
    replace_text(repo, "README.md", "`context:write`", "context-write")
    readme = repo / "README.md"
    text = readme.read_text(encoding="utf-8")
    readme.write_text("[Claude](docs/clients/claude.md)\n\n" + text, encoding="utf-8")
    found = errors(content.check_readme(repo))
    assert any("NOT YET LIVE" in e for e in found)
    assert any("context:write" in e for e in found)
    assert any("privacy guide before" in e for e in found)


def test_examples_must_use_reserved_domains_and_example_cards(repo: Path) -> None:
    def change(data: dict[str, Any]) -> None:
        result = data["steps"][6]["result"]
        result["candidates"][0]["sources"] = ["https://www.realbank.com/card"]
        result["candidates"][0]["slug"] = "real-bank-card"

    edit_json(repo, "examples/shortlist-with-saved-context.json", change)
    found = errors(content.check_examples_synthetic(repo))
    assert any("reserved domain" in e for e in found)
    assert any("real-bank-card" in e for e in found)


def test_example_wallet_cards_are_synthetic(repo: Path) -> None:
    edit_json(
        repo,
        "examples/correct-and-forget.json",
        lambda d: d["steps"][2]["result"]["wallet"].append("real-card"),
    )
    assert any("real-card" in e for e in errors(content.check_examples_synthetic(repo)))
