"""Compatibility table rules: untested surfaces stay unverified."""

from __future__ import annotations

import re
from pathlib import Path

from .common import Finding, read_text
from .constants import CLIENT_GUIDES, CONSUMER_CLIENTS

CHECK = "compatibility"
DOC = "docs/compatibility.md"
COLUMNS = (
    "Client",
    "Tested surface",
    "Account prerequisites",
    "Status",
    "Verification date",
    "Evidence",
)
STATUSES = frozenset({"Unverified", "Verified", "Not supported"})
NOT_VERIFIED = "not yet verified"
ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
LINK = re.compile(r"^\[([^\]]+)\]\(([^)]+)\)$")
ANY_LINK = re.compile(r"\[[^\]]+\]\([^)]+\)")


def split_row(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def parse_tables(text: str) -> list[tuple[int, list[str]]]:
    """Return ``(line_number, cells)`` for every row of tables that use COLUMNS."""
    rows: list[tuple[int, list[str]]] = []
    lines = text.splitlines()
    index = 0
    while index < len(lines):
        if lines[index].lstrip().startswith("|") and tuple(split_row(lines[index])) == COLUMNS:
            index += 2  # skip header and delimiter
            while index < len(lines) and lines[index].lstrip().startswith("|"):
                rows.append((index + 1, split_row(lines[index])))
                index += 1
        else:
            index += 1
    return rows


def check(root: Path) -> list[Finding]:
    text = read_text(root, DOC)
    if text is None:
        return [Finding(CHECK, DOC, "file is missing")]
    findings: list[Finding] = []
    rows = parse_tables(text)
    if not rows:
        findings.append(Finding(CHECK, DOC, f"no table with columns {' | '.join(COLUMNS)}"))
    clients: dict[str, str] = {}
    for number, cells in rows:
        if len(cells) != len(COLUMNS):
            findings.append(
                Finding(CHECK, DOC, f"expected {len(COLUMNS)} cells, got {len(cells)}", line=number)
            )
            continue
        client_cell, surface, prerequisites, status, date, evidence = cells
        link = LINK.match(client_cell)
        client = link.group(1) if link else client_cell
        if not prerequisites:
            findings.append(Finding(CHECK, DOC, f"{client}: prerequisites are empty", line=number))
        if status not in STATUSES:
            findings.append(
                Finding(CHECK, DOC, f"{client}: unknown status '{status}'", line=number)
            )
        elif status == "Verified":
            if not ISO_DATE.match(date):
                findings.append(
                    Finding(CHECK, DOC, f"{client}: Verified needs a YYYY-MM-DD date", line=number)
                )
            if not ANY_LINK.search(evidence):
                findings.append(
                    Finding(CHECK, DOC, f"{client}: Verified needs an evidence link", line=number)
                )
            if surface.lower().startswith("none"):
                findings.append(
                    Finding(CHECK, DOC, f"{client}: Verified needs a tested surface", line=number)
                )
        elif date != NOT_VERIFIED:
            findings.append(
                Finding(
                    CHECK, DOC, f"{client}: {status} rows must say '{NOT_VERIFIED}'", line=number
                )
            )
        clients.setdefault(client, status)
    for client in CONSUMER_CLIENTS:
        if client not in clients:
            findings.append(Finding(CHECK, DOC, f"missing consumer client row: {client}"))
            continue
        guide = CLIENT_GUIDES[client]
        guide_text = read_text(root, guide)
        if guide_text is None:
            findings.append(Finding(CHECK, guide, "client guide is missing"))
            continue
        expected = f"**Status: {clients[client].lower()}.**"
        if expected not in guide_text:
            findings.append(Finding(CHECK, guide, f"guide must state '{expected}' to match {DOC}"))
    return findings
