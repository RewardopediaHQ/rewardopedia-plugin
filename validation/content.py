"""Cross-file consistency: plugin identity, endpoint, tools, scopes and synthetic data."""

from __future__ import annotations

import json
import re
from collections.abc import Iterator
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

from .common import Finding, load_json, read_text, repo_files
from .constants import (
    BRAND_DOMAIN,
    CANONICAL_ENDPOINT,
    CLIENT_GUIDES,
    LICENSE_ID,
    MARKETPLACE,
    MCP_SERVER_NAME,
    PLUGIN_NAME,
    REPOSITORY_URL,
    SCOPES,
    SERVICE_HOST,
    SERVICE_LIVE,
    TOOLS,
)
from .links import is_reserved_example

CHECK = "content"
TOOLS_DOC = "skills/card-recommendations/references/tools.md"
TOOL_HEADING = re.compile(r"^### `([a-z_]+)`", re.MULTILINE)
URL = re.compile(r"https?://[^\s\"'<>)`\]]+")
CODE_URL = re.compile(r"`(https?://[^`\s]+)`")
# Files users read or clients load; validator code and tests may hold bad URLs on purpose.
ENDPOINT_SCAN_SUFFIXES = frozenset({".md", ".json", ".yml", ".yaml"})
NOT_LIVE_BANNER = "NOT YET LIVE"
CARD_KEYS = frozenset({"slug", "cards", "wallet", "walletAdditions", "walletRemovals"})


def check_identity(root: Path) -> list[Finding]:
    findings: list[Finding] = []
    portable, f1 = load_json(root, "plugin.json", CHECK)
    claude, f2 = load_json(root, ".claude-plugin/plugin.json", CHECK)
    marketplace, f3 = load_json(root, MARKETPLACE, CHECK)
    findings.extend([*f1, *f2, *f3])
    manifests = {"plugin.json": portable, ".claude-plugin/plugin.json": claude}
    for relative, data in manifests.items():
        if not isinstance(data, dict):
            continue
        if data.get("name") != PLUGIN_NAME:
            findings.append(Finding(CHECK, relative, f"name must be '{PLUGIN_NAME}'"))
        if data.get("license") != LICENSE_ID:
            findings.append(Finding(CHECK, relative, f"license must be '{LICENSE_ID}'"))
        if data.get("repository") != REPOSITORY_URL:
            findings.append(Finding(CHECK, relative, f"repository must be '{REPOSITORY_URL}'"))
    if (
        isinstance(portable, dict)
        and isinstance(claude, dict)
        and portable.get("description") != claude.get("description")
    ):
        findings.append(
            Finding(CHECK, ".claude-plugin/plugin.json", "description differs from plugin.json")
        )
    if isinstance(marketplace, dict):
        entries = marketplace.get("plugins", [])
        names = [e.get("name") for e in entries if isinstance(e, dict)]
        if names != [PLUGIN_NAME]:
            findings.append(
                Finding(CHECK, MARKETPLACE, f"must list exactly one plugin named '{PLUGIN_NAME}'")
            )
    return findings


def check_endpoints(root: Path) -> list[Finding]:
    findings: list[Finding] = []
    for relative in ("mcp.json", ".mcp.json"):
        data, load_findings = load_json(root, relative, CHECK)
        findings.extend(load_findings)
        if not isinstance(data, dict):
            continue
        servers = data.get("mcpServers")
        if not isinstance(servers, dict) or list(servers) != [MCP_SERVER_NAME]:
            findings.append(
                Finding(CHECK, relative, f"must declare exactly one server '{MCP_SERVER_NAME}'")
            )
            continue
        server = servers[MCP_SERVER_NAME]
        if not isinstance(server, dict) or server.get("url") != CANONICAL_ENDPOINT:
            findings.append(Finding(CHECK, relative, f"server url must be {CANONICAL_ENDPOINT}"))
        if isinstance(server, dict) and ({"headers", "env", "oauth"} & set(server)):
            findings.append(
                Finding(CHECK, relative, "no headers, env or client credentials may be embedded")
            )
    return findings


def check_endpoint_references(root: Path) -> list[Finding]:
    """Every service URL users read is the canonical endpoint, and guides give it verbatim."""
    findings: list[Finding] = []
    for path in repo_files(root):
        if path.suffix not in ENDPOINT_SCAN_SUFFIXES:
            continue
        relative = path.as_posix()
        text = (root / path).read_text(encoding="utf-8")
        for number, line in enumerate(text.splitlines(), start=1):
            for raw in URL.findall(line):
                url = raw.rstrip(".,;:!?")
                host = (urlsplit(url).hostname or "").lower()
                if host == SERVICE_HOST and url != CANONICAL_ENDPOINT:
                    findings.append(
                        Finding(
                            CHECK,
                            relative,
                            f"service URL must be exactly {CANONICAL_ENDPOINT}: {url}",
                            line=number,
                        )
                    )
                elif "rewardopedia" in host and not (
                    host == BRAND_DOMAIN or host.endswith("." + BRAND_DOMAIN)
                ):
                    findings.append(
                        Finding(
                            CHECK, relative, f"lookalike Rewardopedia host: {host}", line=number
                        )
                    )
    for client, guide in CLIENT_GUIDES.items():
        guide_text = read_text(root, guide)
        if guide_text is None:
            continue  # reported by the compatibility check
        if CANONICAL_ENDPOINT not in guide_text:
            findings.append(
                Finding(CHECK, guide, f"{client} guide must give the endpoint {CANONICAL_ENDPOINT}")
            )
        for number, line in enumerate(guide_text.splitlines(), start=1):
            for url in CODE_URL.findall(line):
                if url != CANONICAL_ENDPOINT:
                    findings.append(
                        Finding(
                            CHECK,
                            guide,
                            f"a URL users paste must be {CANONICAL_ENDPOINT}: {url}",
                            line=number,
                        )
                    )
    return findings


def check_tools_doc(root: Path) -> list[Finding]:
    findings: list[Finding] = []
    text = read_text(root, TOOLS_DOC)
    if text is None:
        return [Finding(CHECK, TOOLS_DOC, "tool reference is missing")]
    documented = TOOL_HEADING.findall(text)
    if documented != list(TOOLS):
        findings.append(
            Finding(
                CHECK,
                TOOLS_DOC,
                f"tool headings must be exactly {', '.join(TOOLS)} in order; found "
                f"{', '.join(documented) or 'none'}",
            )
        )
    for scope in SCOPES:
        if f"`{scope}`" not in text:
            findings.append(Finding(CHECK, TOOLS_DOC, f"scope `{scope}` is not documented"))
    schema, load_findings = load_json(root, "schemas/example.schema.json", CHECK)
    findings.extend(load_findings)
    if isinstance(schema, dict):
        enum = schema.get("$defs", {}).get("tool", {}).get("enum")
        if enum != list(TOOLS):
            findings.append(
                Finding(
                    CHECK, "schemas/example.schema.json", "tool enum must list the eleven tools"
                )
            )
    return findings


def check_readme(root: Path) -> list[Finding]:
    text = read_text(root, "README.md")
    if text is None:
        return [Finding(CHECK, "README.md", "file is missing")]
    findings = []
    if SERVICE_LIVE and NOT_LIVE_BANNER in text:
        findings.append(
            Finding(CHECK, "README.md", f"remove the '{NOT_LIVE_BANNER}' banner once live")
        )
    elif not SERVICE_LIVE and NOT_LIVE_BANNER not in text:
        findings.append(Finding(CHECK, "README.md", f"must carry the '{NOT_LIVE_BANNER}' banner"))
    if CANONICAL_ENDPOINT not in text:
        findings.append(Finding(CHECK, "README.md", f"must name the endpoint {CANONICAL_ENDPOINT}"))
    for scope in SCOPES:
        if f"`{scope}`" not in text:
            findings.append(Finding(CHECK, "README.md", f"scope `{scope}` is not explained"))
    privacy = text.find("docs/privacy-and-memory.md")
    setup = text.find("docs/clients/")
    if privacy == -1 or (setup != -1 and privacy > setup):
        findings.append(
            Finding(CHECK, "README.md", "link the privacy guide before any client setup guide")
        )
    return findings


def _strings(data: Any, key: str | None = None) -> Iterator[tuple[str | None, str]]:
    """Yield ``(nearest_key, value)`` for every string in a JSON document."""
    if isinstance(data, str):
        yield key, data
    elif isinstance(data, dict):
        for inner_key, value in data.items():
            yield from _strings(value, inner_key)
    elif isinstance(data, list):
        for item in data:
            yield from _strings(item, key)


def check_examples_synthetic(root: Path) -> list[Finding]:
    findings: list[Finding] = []
    for path in repo_files(root):
        if path.parts[0] != "examples" or path.suffix != ".json":
            continue
        relative = path.as_posix()
        try:
            data = json.loads((root / path).read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue  # reported by the schema check
        for key, value in _strings(data):
            for url in URL.findall(value):
                host = urlsplit(url).hostname or ""
                if not is_reserved_example(host):
                    findings.append(
                        Finding(CHECK, relative, f"example URL must use a reserved domain: {url}")
                    )
            if key in CARD_KEYS and not value.startswith("example-"):
                findings.append(
                    Finding(CHECK, relative, f"example card id must start 'example-': {value}")
                )
    return findings


def check_examples_notice(root: Path) -> list[Finding]:
    """The assistant speaks (the request-history notice) before an example's first tool call."""
    findings: list[Finding] = []
    for path in repo_files(root):
        if path.parts[0] != "examples" or path.suffix != ".json":
            continue
        try:
            data = json.loads((root / path).read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue  # reported by the schema check
        steps = data.get("steps") if isinstance(data, dict) else None
        if not isinstance(steps, list):
            continue  # reported by the schema check
        actors = [step.get("actor") for step in steps if isinstance(step, dict)]
        if "tool_call" in actors and "assistant" not in actors[: actors.index("tool_call")]:
            findings.append(
                Finding(
                    CHECK,
                    path.as_posix(),
                    "give the request-history notice in an assistant step before the first "
                    "tool call",
                )
            )
    return findings


def check(root: Path) -> list[Finding]:
    return [
        *check_identity(root),
        *check_endpoints(root),
        *check_endpoint_references(root),
        *check_tools_doc(root),
        *check_readme(root),
        *check_examples_synthetic(root),
        *check_examples_notice(root),
    ]
