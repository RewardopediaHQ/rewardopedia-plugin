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

CHECK = "schemas"

VENDOR_DIR = "schemas/vendor/agent-plugins-1.0.0"
VENDOR_HASHES = {
    f"{VENDOR_DIR}/plugin.schema.json": (
        "0a4aad95ce337878ad38802ebf0daa3fde76abe3f65400c86bcbb1ec0b3ab883"
    ),
    f"{VENDOR_DIR}/mcp.schema.json": (
        "6539175bfcdf43085855183e86da40ea94b166547a72b47ae9a0a390516d3acb"
    ),
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


def check(root: Path) -> list[Finding]:
    return [
        *check_syntax(root),
        *check_vendor_hashes(root),
        *check_manifests(root),
        *check_skills(root),
        *check_examples(root),
    ]
