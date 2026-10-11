"""JSON and YAML syntax plus JSON Schema validation for manifests, skills and examples."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator

from .common import Finding, load_json, repo_files
from .constants import TOOLS

CHECK = "schemas"

VENDOR_DIR = "schemas/vendor/agent-plugins-1.0.0"
# The server's advertised tool contract, exported from the Rewardopedia monorepo.
TOOL_SNAPSHOT = "schemas/vendor/rewardopedia-mcp/tools.json"
VENDOR_HASHES = {
    f"{VENDOR_DIR}/plugin.schema.json": (
        "0a4aad95ce337878ad38802ebf0daa3fde76abe3f65400c86bcbb1ec0b3ab883"
    ),
    f"{VENDOR_DIR}/mcp.schema.json": (
        "6539175bfcdf43085855183e86da40ea94b166547a72b47ae9a0a390516d3acb"
    ),
    TOOL_SNAPSHOT: "23e2a06c7208825ac1a6aad3910f5a5d4330fe720ba500ed22046cb7a100d923",
}

# Manifest file -> schema file.
MANIFEST_SCHEMAS = {
    "plugin.json": f"{VENDOR_DIR}/plugin.schema.json",
    "mcp.json": f"{VENDOR_DIR}/mcp.schema.json",
    ".claude-plugin/plugin.json": "schemas/claude-plugin.schema.json",
    ".claude-plugin/marketplace.json": "schemas/claude-marketplace.schema.json",
    ".mcp.json": "schemas/claude-mcp.schema.json",
}
SKILL_SCHEMA = "schemas/skill-frontmatter.schema.json"
EXAMPLE_SCHEMA = "schemas/example.schema.json"

FRONTMATTER = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)


def _validator(root: Path, schema_path: str) -> tuple[Draft202012Validator | None, list[Finding]]:
    schema, findings = load_json(root, schema_path, CHECK)
    if schema is None:
        return None, findings
    try:
        Draft202012Validator.check_schema(schema)
    except Exception as error:  # jsonschema raises SchemaError subclasses
        return None, [Finding(CHECK, schema_path, f"not a valid JSON Schema: {error}")]
    return Draft202012Validator(schema, format_checker=Draft202012Validator.FORMAT_CHECKER), []


def _schema_errors(validator: Draft202012Validator, instance: Any, relative: str) -> list[Finding]:
    findings = []
    for error in sorted(validator.iter_errors(instance), key=lambda e: list(e.absolute_path)):
        pointer = "/" + "/".join(str(part) for part in error.absolute_path)
        findings.append(Finding(CHECK, relative, f"{pointer}: {error.message}"))
    return findings


def check_syntax(root: Path) -> list[Finding]:
    """Every JSON and YAML file in the repository must parse."""
    findings: list[Finding] = []
    for path in repo_files(root):
        if path.suffix not in {".json", ".yml", ".yaml"}:
            continue
        relative = path.as_posix()
        text = (root / path).read_text(encoding="utf-8")
        if path.suffix == ".json":
            try:
                json.loads(text)
            except json.JSONDecodeError as error:
                findings.append(
                    Finding(CHECK, relative, f"invalid JSON: {error.msg}", line=error.lineno)
                )
        else:
            try:
                yaml.safe_load(text)
            except yaml.YAMLError as error:
                line = None
                mark = getattr(error, "problem_mark", None)
                if mark is not None:
                    line = mark.line + 1
                findings.append(Finding(CHECK, relative, f"invalid YAML: {error}", line=line))
    return findings


def check_vendor_hashes(root: Path) -> list[Finding]:
    findings = []
    for relative, expected in VENDOR_HASHES.items():
        path = root / relative
        if not path.is_file():
            findings.append(Finding(CHECK, relative, "vendored schema is missing"))
            continue
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual != expected:
            findings.append(
                Finding(CHECK, relative, "vendored schema changed; update schemas/vendor/README.md")
            )
    return findings


def check_manifests(root: Path) -> list[Finding]:
    findings: list[Finding] = []
    for manifest, schema_path in MANIFEST_SCHEMAS.items():
        validator, schema_findings = _validator(root, schema_path)
        findings.extend(schema_findings)
        data, load_findings = load_json(root, manifest, CHECK)
        findings.extend(load_findings)
        if validator is not None and data is not None:
            findings.extend(_schema_errors(validator, data, manifest))
    return findings


def parse_frontmatter(text: str) -> tuple[Any, str | None]:
    """Return ``(frontmatter, error)`` for a SKILL.md document."""
    match = FRONTMATTER.match(text)
    if match is None:
        return None, "missing YAML frontmatter delimited by '---' lines"
    try:
        return yaml.safe_load(match.group(1)), None
    except yaml.YAMLError as error:
        return None, f"invalid YAML frontmatter: {error}"


def check_skills(root: Path) -> list[Finding]:
    validator, findings = _validator(root, SKILL_SCHEMA)
    skill_files = [p for p in repo_files(root) if p.name == "SKILL.md"]
    if not skill_files:
        findings.append(Finding(CHECK, "skills/", "no skills/<name>/SKILL.md found"))
    for path in skill_files:
        relative = path.as_posix()
        if len(path.parts) != 3 or path.parts[0] != "skills":
            findings.append(Finding(CHECK, relative, "skills must live at skills/<name>/SKILL.md"))
            continue
        frontmatter, error = parse_frontmatter((root / path).read_text(encoding="utf-8"))
        if error is not None:
            findings.append(Finding(CHECK, relative, error))
            continue
        if validator is not None:
            findings.extend(_schema_errors(validator, frontmatter, relative))
        if isinstance(frontmatter, dict) and frontmatter.get("name") != path.parts[1]:
            findings.append(
                Finding(CHECK, relative, "frontmatter name must match the skill directory name")
            )
    return findings


def check_examples(root: Path) -> list[Finding]:
    validator, findings = _validator(root, EXAMPLE_SCHEMA)
    examples = [p for p in repo_files(root) if p.parts[0] == "examples" and p.suffix == ".json"]
    if not examples:
        findings.append(Finding(CHECK, "examples/", "no synthetic examples found"))
    for path in examples:
        relative = path.as_posix()
        data, load_findings = load_json(root, relative, CHECK)
        findings.extend(load_findings)
        if validator is not None and data is not None:
            findings.extend(_schema_errors(validator, data, relative))
    return findings


def load_tool_snapshot(root: Path) -> tuple[dict[str, dict[str, Any]], list[Finding]]:
    """Return the vendored tool contract keyed by tool name, checked against TOOLS."""
    data, findings = load_json(root, TOOL_SNAPSHOT, CHECK)
    if not isinstance(data, dict) or not isinstance(data.get("tools"), list):
        if data is not None:
            findings.append(Finding(CHECK, TOOL_SNAPSHOT, "must hold a 'tools' list"))
        return {}, findings
    tools = {t["name"]: t for t in data["tools"] if isinstance(t, dict) and "name" in t}
    if list(tools) != list(TOOLS):
        findings.append(
            Finding(
                CHECK,
                TOOL_SNAPSHOT,
                f"tools must be exactly {', '.join(TOOLS)} in order; found {', '.join(tools)}",
            )
        )
    for name, tool in tools.items():
        schema = tool.get("inputSchema")
        if not isinstance(schema, dict):
            findings.append(Finding(CHECK, TOOL_SNAPSHOT, f"{name}: inputSchema is missing"))
            continue
        try:
            Draft202012Validator.check_schema(schema)
        except Exception as error:  # jsonschema raises SchemaError subclasses
            findings.append(Finding(CHECK, TOOL_SNAPSHOT, f"{name}: invalid inputSchema: {error}"))
    return tools, findings


def _strict_arguments(schema: dict[str, Any]) -> Draft202012Validator:
    # The server ignores unknown top-level arguments; an example must not invent any.
    return Draft202012Validator(
        {**schema, "additionalProperties": False},
        format_checker=Draft202012Validator.FORMAT_CHECKER,
    )


def check_example_calls(root: Path) -> list[Finding]:
    """Example tool calls use the server's real arguments; results only its real fields."""
    tools, findings = load_tool_snapshot(root)
    if not tools:
        return findings
    for path in repo_files(root):
        if path.parts[0] != "examples" or path.suffix != ".json":
            continue
        relative = path.as_posix()
        data, load_findings = load_json(root, relative, CHECK)
        if load_findings or not isinstance(data, dict):
            continue  # reported by check_examples
        for index, step in enumerate(data.get("steps") or []):
            if not isinstance(step, dict) or step.get("tool") not in tools:
                continue
            tool = tools[step["tool"]]
            where = f"/steps/{index}"
            if step.get("actor") == "tool_call" and isinstance(tool.get("inputSchema"), dict):
                validator = _strict_arguments(tool["inputSchema"])
                for error in sorted(
                    validator.iter_errors(step.get("arguments")), key=lambda e: e.json_path
                ):
                    pointer = "/" + "/".join(str(part) for part in error.absolute_path)
                    findings.append(
                        Finding(
                            CHECK,
                            relative,
                            f"{where}/arguments{pointer}: {step['tool']} {error.message}",
                        )
                    )
            elif step.get("actor") == "tool_result" and isinstance(step.get("result"), dict):
                unknown = sorted(set(step["result"]) - set(tool.get("outputProperties", [])))
                if unknown:
                    findings.append(
                        Finding(
                            CHECK,
                            relative,
                            f"{where}/result has fields {step['tool']} does not return: "
                            f"{', '.join(unknown)}",
                        )
                    )
    return findings


def check(root: Path) -> list[Finding]:
    return [
        *check_syntax(root),
        *check_vendor_hashes(root),
        *check_manifests(root),
        *check_skills(root),
        *check_examples(root),
        *check_example_calls(root),
    ]
