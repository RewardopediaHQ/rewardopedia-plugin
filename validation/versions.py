"""Manifest, changelog and release-tag version consistency.

Rules:

* Every versioned manifest (and any marketplace entry that sets ``version``)
  carries the same Semantic Versioning 2.0.0 string.
* ``CHANGELOG.md`` always has an ``## [Unreleased]`` section.
* Untagged builds carry either a ``-dev`` pre-release (normal development) or
  a release version whose dated changelog section already exists (release
  preparation).
* A ``vX.Y.Z`` tag build must match the manifest version exactly, must not be a
  pre-release, and needs a dated ``## [X.Y.Z] - YYYY-MM-DD`` section.
"""

from __future__ import annotations

import os
import re
from pathlib import Path

from .common import Finding, load_json, read_text
from .constants import MARKETPLACE, VERSIONED_MANIFESTS

CHECK = "versions"

SEMVER = re.compile(
    r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
    r"(?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?"
    r"(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$"
)
DEV_VERSION = re.compile(r"^\d+\.\d+\.\d+-dev(?:\.\d+)?$")
RELEASE_VERSION = re.compile(r"^\d+\.\d+\.\d+$")
UNRELEASED_HEADING = re.compile(r"^## \[Unreleased\]\s*$", re.MULTILINE)
RELEASE_HEADING = re.compile(r"^## \[(?P<version>[^\]]+)\](?P<rest>.*)$", re.MULTILINE)
DATED = re.compile(r"^ - \d{4}-\d{2}-\d{2}$")
TAG_REF = re.compile(r"^refs/tags/(?P<tag>.+)$")


def manifest_versions(root: Path) -> tuple[dict[str, str], list[Finding]]:
    """Collect ``{location: version}`` from every place a version is declared."""
    versions: dict[str, str] = {}
    findings: list[Finding] = []
    for manifest in VERSIONED_MANIFESTS:
        data, load_findings = load_json(root, manifest, CHECK)
        findings.extend(load_findings)
        if data is None:
            continue
        version = data.get("version") if isinstance(data, dict) else None
        if not isinstance(version, str):
            findings.append(Finding(CHECK, manifest, "missing string 'version'"))
            continue
        versions[manifest] = version
    data, load_findings = load_json(root, MARKETPLACE, CHECK)
    findings.extend(load_findings)
    if isinstance(data, dict):
        for index, entry in enumerate(data.get("plugins", [])):
            if isinstance(entry, dict) and "version" in entry:
                versions[f"{MARKETPLACE} plugins[{index}]"] = str(entry["version"])
    return versions, findings


def changelog_sections(text: str) -> dict[str, str]:
    """Map each ``## [version]`` heading to the remainder of its heading line."""
    return {m.group("version"): m.group("rest") for m in RELEASE_HEADING.finditer(text)}


def release_notes(changelog: str, version: str) -> str:
    """Return the body of the dated ``## [version]`` section, for release notes.

    Raises ``ValueError`` when the section is missing, undated or empty.
    """
    headings = list(RELEASE_HEADING.finditer(changelog))
    for index, heading in enumerate(headings):
        if heading.group("version") != version:
            continue
        if not DATED.match(heading.group("rest")):
            raise ValueError(f"release '{version}' needs ' - YYYY-MM-DD'")
        end = headings[index + 1].start() if index + 1 < len(headings) else len(changelog)
        body = changelog[heading.end() : end].strip()
        # Drop trailing link reference definitions shared by the whole changelog.
        body = re.sub(r"(?:\n\[[^\]]+\]: \S+)+$", "", body).strip()
        if not body:
            raise ValueError(f"release '{version}' has no changelog entries")
        return body + "\n"
    raise ValueError(f"CHANGELOG.md has no '## [{version}] - YYYY-MM-DD' section")


def check(root: Path, ref: str | None = None) -> list[Finding]:
    if ref is None:
        ref = os.environ.get("GITHUB_REF", "")
    versions, findings = manifest_versions(root)
    for location, version in versions.items():
        if not SEMVER.match(version):
            findings.append(
                Finding(CHECK, location, f"'{version}' is not a Semantic Versioning 2.0.0 string")
            )
    distinct = sorted(set(versions.values()))
    if len(distinct) > 1:
        detail = ", ".join(f"{loc}={ver}" for loc, ver in sorted(versions.items()))
        findings.append(Finding(CHECK, "plugin.json", f"manifest versions differ: {detail}"))
        return findings
    if not distinct:
        return findings
    version = distinct[0]

    changelog = read_text(root, "CHANGELOG.md")
    if changelog is None:
        findings.append(Finding(CHECK, "CHANGELOG.md", "file is missing"))
        return findings
    if not UNRELEASED_HEADING.search(changelog):
        findings.append(Finding(CHECK, "CHANGELOG.md", "missing '## [Unreleased]' section"))
    sections = changelog_sections(changelog)
    for heading, rest in sections.items():
        if heading == "Unreleased":
            continue
        if not RELEASE_VERSION.match(heading):
            findings.append(
                Finding(CHECK, "CHANGELOG.md", f"release heading '{heading}' is not X.Y.Z")
            )
        elif not DATED.match(rest):
            findings.append(
                Finding(CHECK, "CHANGELOG.md", f"release '{heading}' needs ' - YYYY-MM-DD'")
            )

    tag_match = TAG_REF.match(ref or "")
    if tag_match:
        tag = tag_match.group("tag")
        if tag != f"v{version}":
            findings.append(
                Finding(CHECK, "plugin.json", f"tag '{tag}' does not match version '{version}'")
            )
        if not RELEASE_VERSION.match(version):
            findings.append(
                Finding(CHECK, "plugin.json", f"cannot tag pre-release version '{version}'")
            )
        if version not in sections:
            findings.append(
                Finding(CHECK, "CHANGELOG.md", f"missing '## [{version}] - YYYY-MM-DD' for tag")
            )
    elif DEV_VERSION.match(version):
        base = version.split("-", 1)[0]
        if base in sections:
            findings.append(
                Finding(
                    CHECK,
                    "CHANGELOG.md",
                    f"'{base}' is already released; bump the -dev version past it",
                )
            )
    elif RELEASE_VERSION.match(version):
        if version not in sections:
            findings.append(
                Finding(
                    CHECK,
                    "plugin.json",
                    f"untagged release version '{version}' needs a dated changelog section; "
                    "use an X.Y.Z-dev version during development",
                )
            )
    else:
        findings.append(
            Finding(
                CHECK,
                "plugin.json",
                f"version '{version}' must be X.Y.Z-dev during development or X.Y.Z for release",
            )
        )
    return findings
