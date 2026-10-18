"""Stable releases need shared acceptance and one independently verified surface."""

from __future__ import annotations

import os
import re
from datetime import date
from pathlib import Path
from urllib.parse import urlsplit

from . import compat
from .common import Finding, load_json, read_text
from .constants import CONSUMER_CLIENTS, SERVICE_LIVE, TOOLS

CHECK = "release"
READINESS = "release-readiness.json"
SURFACES = {*CONSUMER_CLIENTS, "Claude Code", "Codex", "ChatGPT desktop", "Grok Build"}


def https_url(value: object) -> bool:
    if not isinstance(value, str):
        return False
    try:
        parsed = urlsplit(value)
        return (
            parsed.scheme == "https"
            and bool(parsed.hostname)
            and not (parsed.username or parsed.password)
        )
    except ValueError:
        return False


def nested_object(value: object, key: str, path: str, findings: list[Finding]) -> dict:
    """Return mapping ``value[key]``; a present but non-object value is an error."""
    if not isinstance(value, dict):
        return {}
    child = value.get(key)
    if child is None:
        return {}
    if not isinstance(child, dict):
        findings.append(Finding(CHECK, "plugin.json", f"{path} must be a JSON object"))
        return {}
    return child


def check(root: Path, ref: str | None = None) -> list[Finding]:
    manifest, findings = load_json(root, "plugin.json", CHECK)
    if not isinstance(manifest, dict):
        if not findings:
            findings.append(Finding(CHECK, "plugin.json", "manifest must be a JSON object"))
        return findings
    extensions = nested_object(manifest, "extensions", "extensions", findings)
    openai_ext = nested_object(extensions, "com.openai", "extensions.com.openai", findings)
    interface = nested_object(openai_ext, "interface", "extensions.com.openai.interface", findings)
    for field in ("displayName", "shortDescription"):
        value = interface.get(field)
        if not isinstance(value, str) or not 1 <= len(value) <= 30:
            findings.append(Finding(CHECK, "plugin.json", f"{field} needs 1-30 characters"))
    for field in ("websiteURL", "supportURL", "privacyPolicyURL", "termsOfServiceURL"):
        if not https_url(interface.get(field)):
            findings.append(Finding(CHECK, "plugin.json", f"{field} needs a public HTTPS URL"))
    for field in ("logo", "composerIcon"):
        value = interface.get(field)
        if (
            not isinstance(value, str)
            or not value.startswith("./assets/")
            or ".." in Path(value).parts
            or not (root / value).is_file()
        ):
            findings.append(Finding(CHECK, "plugin.json", f"{field} needs a bundled assets file"))
    review = nested_object(openai_ext, "review", "extensions.com.openai.review", findings)
    cases = nested_object(review, "test_cases", "extensions.com.openai.review.test_cases", findings)
    for kind, count in (("positive", 5), ("negative", 3)):
        rows = cases.get(kind)
        if not isinstance(rows, list) or len(rows) != count:
            findings.append(Finding(CHECK, "plugin.json", f"need {count} {kind} review cases"))
            continue
        for row in rows:
            fields = ("description", "prompt", "expected_behavior")
            if not isinstance(row, dict) or any(
                not isinstance(row.get(key), str) or not row[key].strip() for key in fields
            ):
                findings.append(Finding(CHECK, "plugin.json", f"incomplete {kind} review case"))
                continue
            if kind == "positive":
                tools = row.get("tools_triggered")
                if (
                    not isinstance(tools, str)
                    or not tools.strip()
                    or any(name.strip() not in TOOLS for name in tools.split(","))
                ):
                    findings.append(Finding(CHECK, "plugin.json", "unknown review case tools"))

    version = manifest.get("version", "")
    stable = isinstance(version, str) and bool(re.fullmatch(r"\d+\.\d+\.\d+", version))
    tagged = (ref if ref is not None else os.environ.get("GITHUB_REF", "")).startswith("refs/tags/")
    if not (stable or tagged):
        return findings
    readiness, errors = load_json(root, READINESS, CHECK)
    findings.extend(errors)
    if not isinstance(readiness, dict):
        return [*findings, Finding(CHECK, READINESS, "shared acceptance record is required")]
    backend = readiness.get("sharedBackend", {})
    if not isinstance(backend, dict):
        backend = {}
    try:
        verified = date.fromisoformat(str(backend.get("verifiedAt"))) <= date.today()
    except ValueError:
        verified = False
    evidence = backend.get("evidence")
    if (
        not SERVICE_LIVE
        or readiness.get("version") != version
        or backend.get("status") != "accepted"
        or not verified
        or not re.fullmatch(r"[0-9a-f]{40}", str(backend.get("serviceCommit")))
        or not isinstance(evidence, list)
        or not evidence
        or not all(https_url(link) for link in evidence)
    ):
        findings.append(
            Finding(CHECK, READINESS, "version-pinned shared backend acceptance required")
        )
    rows = compat.parse_tables(read_text(root, compat.DOC) or "")
    qualified = []
    for _, cells in rows:
        if len(cells) != len(compat.COLUMNS):
            continue
        link = compat.LINK.match(cells[0])
        client = link.group(1) if link else cells[0]
        if client in SURFACES and cells[3] == "Verified":
            qualified.append(client)
    if not qualified or compat.check(root):
        findings.append(Finding(CHECK, compat.DOC, "at least one valid verified surface required"))
    return findings
