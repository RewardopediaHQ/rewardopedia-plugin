"""Simulated maintainer steps from CONTRIBUTING.md and docs/compatibility.md.

Each step edits a repository copy the way a maintainer would: recording a
client verification, launching the service, cutting a release and starting the
next development cycle. Steps derive versions from the copy, so they keep
working after real releases.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from validation import compat, content
from validation.constants import CLIENT_GUIDES, VERSIONED_MANIFESTS

STEP_DATE = "2026-10-15"
EVIDENCE = "[run 1](https://github.com/RewardopediaHQ/rewardopedia-plugin/issues/1)"
GUIDE_STATUS = re.compile(r"\*\*Status: [a-z ]+\.\*\*")


def current_version(root: Path) -> str:
    data = json.loads((root / VERSIONED_MANIFESTS[0]).read_text(encoding="utf-8"))
    return str(data["version"])


def set_version(root: Path, version: str) -> None:
    for manifest in VERSIONED_MANIFESTS:
        path = root / manifest
        data = json.loads(path.read_text(encoding="utf-8"))
        data["version"] = version
        path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def verify_client(root: Path, client: str = "ChatGPT") -> None:
    """Record a verified row with date and evidence, and update the guide's status."""
    doc = root / compat.DOC
    lines = doc.read_text(encoding="utf-8").splitlines(keepends=True)
    for index, line in enumerate(lines):
        if line.startswith(f"| [{client}]("):
            link = compat.split_row(line)[0]
            lines[index] = (
                f"| {link} | web app, remote MCP connection | Rewardopedia account | Verified | "
                f"{STEP_DATE} | {EVIDENCE} |\n"
            )
            break
    else:
        raise AssertionError(f"no {client} row in {compat.DOC}")
    doc.write_text("".join(lines), encoding="utf-8")
    guide = root / CLIENT_GUIDES[client]
    text, count = GUIDE_STATUS.subn("**Status: verified.**", guide.read_text(encoding="utf-8"), 1)
    assert count == 1, f"no status line in {guide}"
    guide.write_text(text, encoding="utf-8")


def launch_service(root: Path) -> None:
    """Flip SERVICE_LIVE and remove the README paragraph carrying the banner."""
    constants = root / "validation/constants.py"
    text = constants.read_text(encoding="utf-8")
    constants.write_text(
        text.replace("SERVICE_LIVE = False", "SERVICE_LIVE = True", 1), encoding="utf-8"
    )
    readme = root / "README.md"
    paragraphs = readme.read_text(encoding="utf-8").split("\n\n")
    kept = [p for p in paragraphs if content.NOT_LIVE_BANNER not in p]
    readme.write_text("\n\n".join(kept), encoding="utf-8")


def cut_release(root: Path) -> str:
    """Prepare the release commit for the current -dev version and return its tag ref."""
    version = current_version(root).split("-", 1)[0]
    set_version(root, version)
    changelog = root / "CHANGELOG.md"
    text = changelog.read_text(encoding="utf-8")
    if f"## [{version}]" not in text:
        text = text.replace(
            "## [Unreleased]\n", f"## [Unreleased]\n\n## [{version}] - {STEP_DATE}\n", 1
        )
        changelog.write_text(text, encoding="utf-8")
    return f"refs/tags/v{version}"


def start_next_cycle(root: Path) -> str:
    """Bump to the next patch -dev version after a release and return it."""
    major, minor, patch = (int(part) for part in current_version(root).split("-")[0].split("."))
    version = f"{major}.{minor}.{patch + 1}-dev"
    set_version(root, version)
    return version
