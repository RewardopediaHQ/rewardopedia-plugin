"""Schema and syntax validation rejects malformed manifests, skills and examples."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from validation import schemas

from .conftest import edit_json, errors, replace_text


def test_invalid_json_is_reported(repo: Path) -> None:
    (repo / "plugin.json").write_text('{"name": "rewardopedia",}\n', encoding="utf-8")
    assert any("plugin.json" in e and "invalid JSON" in e for e in errors(schemas.check(repo)))


def test_invalid_yaml_is_reported(repo: Path) -> None:
    (repo / ".github/workflows/validate.yml").write_text("jobs: [unclosed\n", encoding="utf-8")
    assert any("invalid YAML" in e for e in errors(schemas.check_syntax(repo)))


def test_portable_manifest_requires_agent_plugins_schema(repo: Path) -> None:
    def change(data: dict[str, Any]) -> None:
        data["$schema"] = "https://example.com/other.json"
        data["unexpected"] = True

    edit_json(repo, "plugin.json", change)
    found = errors(schemas.check_manifests(repo))
    assert any("plugin.json" in e and "$schema" in e for e in found)
    assert any("unexpected" in e for e in found)


def test_portable_mcp_requires_transport_type(repo: Path) -> None:
    edit_json(repo, "mcp.json", lambda d: d["mcpServers"]["rewardopedia"].pop("type"))
    assert any(
        e.startswith("ERROR [schemas] mcp.json") for e in errors(schemas.check_manifests(repo))
    )


def test_claude_mcp_requires_http_type(repo: Path) -> None:
    edit_json(repo, ".mcp.json", lambda d: d["mcpServers"]["rewardopedia"].update(type="sse"))
    assert any(".mcp.json" in e for e in errors(schemas.check_manifests(repo)))


def test_claude_manifest_rejects_unknown_fields_and_bad_urls(repo: Path) -> None:
    def change(data: dict[str, Any]) -> None:
        data["homepage"] = "not a url"
        data["bogus"] = 1

    edit_json(repo, ".claude-plugin/plugin.json", change)
    found = errors(schemas.check_manifests(repo))
    assert any("homepage" in e for e in found)
    assert any("bogus" in e for e in found)


def test_marketplace_source_cannot_escape_root(repo: Path) -> None:
    edit_json(
        repo,
        ".claude-plugin/marketplace.json",
        lambda d: d["plugins"][0].update(source="./../elsewhere"),
    )
    assert any("marketplace.json" in e for e in errors(schemas.check_manifests(repo)))


def test_skill_name_must_match_directory(repo: Path) -> None:
    replace_text(
        repo,
        "skills/card-recommendations/SKILL.md",
        "name: card-recommendations",
        "name: other-skill",
    )
    assert any("match the skill directory" in e for e in errors(schemas.check_skills(repo)))


def test_skill_description_length_is_limited(repo: Path) -> None:
    skill = repo / "skills/card-recommendations/SKILL.md"
    text = skill.read_text(encoding="utf-8")
    start = text.index("description: ")
    end = text.index("\n", start)
    skill.write_text(text[:start] + "description: " + "x" * 1025 + text[end:], encoding="utf-8")
    assert any("description" in e for e in errors(schemas.check_skills(repo)))


def test_skill_requires_frontmatter(repo: Path) -> None:
    (repo / "skills/card-recommendations/SKILL.md").write_text("# No frontmatter\n", "utf-8")
    assert any("frontmatter" in e for e in errors(schemas.check_skills(repo)))


def test_example_must_be_synthetic_and_use_known_tools(repo: Path) -> None:
    def change(data: dict[str, Any]) -> None:
        data["synthetic"] = False
        data["steps"][1]["tool"] = "delete_everything"

    edit_json(repo, "examples/needs-input.json", change)
    found = errors(schemas.check_examples(repo))
    assert any("/synthetic" in e for e in found)
    assert any("/steps/1" in e for e in found)


def test_example_locale_is_limited_to_supported_pairs(repo: Path) -> None:
    edit_json(repo, "examples/needs-input.json", lambda d: d.update(locale="en-GB"))
    assert any("/locale" in e for e in errors(schemas.check_examples(repo)))


def test_vendored_schema_changes_are_detected(repo: Path) -> None:
    path = repo / "schemas/vendor/agent-plugins-1.0.0/plugin.schema.json"
    path.write_text(path.read_text(encoding="utf-8") + "\n", encoding="utf-8")
    assert any("vendored schema changed" in e for e in errors(schemas.check_vendor_hashes(repo)))


def test_example_arguments_follow_the_server_input_schema(repo: Path) -> None:
    def change(data: dict[str, Any]) -> None:
        arguments = data["steps"][2]["arguments"]
        arguments["locale"] = arguments.pop("contentLocale")
        arguments["hardConstraints"] = {"maxAnnualFeeUsd": 95}

    edit_json(repo, "examples/needs-input.json", change)
    found = errors(schemas.check_example_calls(repo))
    assert any("'contentLocale' is a required property" in e for e in found)
    assert any("'hardConstraints', 'locale' were unexpected" in e for e in found)


def test_example_argument_values_are_validated(repo: Path) -> None:
    def change(data: dict[str, Any]) -> None:
        data["steps"][6]["arguments"]["requestId"] = "not-a-uuid"

    edit_json(repo, "examples/correct-and-forget.json", change)
    assert any(
        "/steps/6/arguments/requestId" in e for e in errors(schemas.check_example_calls(repo))
    )


def test_example_results_use_only_returned_fields(repo: Path) -> None:
    edit_json(
        repo,
        "examples/needs-input.json",
        lambda d: d["steps"][3]["result"].update(excluded=[]),
    )
    assert any("does not return: excluded" in e for e in errors(schemas.check_example_calls(repo)))


def test_tool_snapshot_must_list_the_eleven_tools(repo: Path) -> None:
    edit_json(repo, schemas.TOOL_SNAPSHOT, lambda d: d["tools"].pop())
    assert any("tools must be exactly" in e for e in errors(schemas.load_tool_snapshot(repo)[1]))


def test_current_examples_match_the_tool_snapshot(repo: Path) -> None:
    assert errors(schemas.check_example_calls(repo)) == []
