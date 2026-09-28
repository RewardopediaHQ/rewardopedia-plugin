"""Compatibility claims need evidence; untested surfaces stay unverified.

Tests write a synthetic compatibility table and guide status lines, so they
pass whatever the repository's real verification state is.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from validation import compat
from validation.constants import CLIENT_GUIDES, CONSUMER_CLIENTS

from .conftest import errors, write_text

HEADER = "| " + " | ".join(compat.COLUMNS) + " |\n" + "| --- " * len(compat.COLUMNS) + "|\n"
EVIDENCE = "[run 1](https://github.com/RewardopediaHQ/rewardopedia-plugin/issues/1)"


def row(
    client: str,
    status: str = "Unverified",
    date: str = compat.NOT_VERIFIED,
    evidence: str = "none",
    surface: str = "none yet (target: web app)",
    prerequisites: str = "Rewardopedia account",
) -> str:
    link = f"[{client}](clients/{client.lower()}.md)"
    return f"| {link} | {surface} | {prerequisites} | {status} | {date} | {evidence} |\n"


def write_state(root: Path, rows: dict[str, str], statuses: dict[str, str]) -> None:
    """Write the table from ``rows`` and each guide with its ``statuses`` value."""
    write_text(root, compat.DOC, "# Client compatibility\n\n" + HEADER + "".join(rows.values()))
    for client, guide in CLIENT_GUIDES.items():
        write_text(root, guide, f"# {client}\n\n**Status: {statuses[client]}.** Synthetic.\n")


@pytest.fixture
def rows() -> dict[str, str]:
    return {client: row(client) for client in CONSUMER_CLIENTS}


@pytest.fixture
def statuses() -> dict[str, str]:
    return dict.fromkeys(CONSUMER_CLIENTS, "unverified")


def test_all_unverified_state_passes(
    repo: Path, rows: dict[str, str], statuses: dict[str, str]
) -> None:
    write_state(repo, rows, statuses)
    assert errors(compat.check(repo)) == []


def test_verified_without_date_or_evidence_is_rejected(
    repo: Path, rows: dict[str, str], statuses: dict[str, str]
) -> None:
    rows["ChatGPT"] = row("ChatGPT", status="Verified", date="soon", surface="none")
    statuses["ChatGPT"] = "verified"
    write_state(repo, rows, statuses)
    found = errors(compat.check(repo))
    assert any("YYYY-MM-DD" in e for e in found)
    assert any("evidence link" in e for e in found)
    assert any("tested surface" in e for e in found)


def test_unverified_row_cannot_carry_a_date(
    repo: Path, rows: dict[str, str], statuses: dict[str, str]
) -> None:
    rows["ChatGPT"] = row("ChatGPT", date="2026-09-27")
    write_state(repo, rows, statuses)
    assert any(compat.NOT_VERIFIED in e for e in errors(compat.check(repo)))


def test_unknown_status_is_rejected(
    repo: Path, rows: dict[str, str], statuses: dict[str, str]
) -> None:
    rows["ChatGPT"] = row("ChatGPT", status="Works")
    write_state(repo, rows, statuses)
    assert any("unknown status" in e for e in errors(compat.check(repo)))


def test_prerequisites_are_required(
    repo: Path, rows: dict[str, str], statuses: dict[str, str]
) -> None:
    rows["Claude"] = row("Claude", prerequisites="")
    write_state(repo, rows, statuses)
    assert any("prerequisites are empty" in e for e in errors(compat.check(repo)))


def test_every_consumer_client_needs_a_row(
    repo: Path, rows: dict[str, str], statuses: dict[str, str]
) -> None:
    del rows["ChatGPT"]
    write_state(repo, rows, statuses)
    assert any("missing consumer client row: ChatGPT" in e for e in errors(compat.check(repo)))


def test_guide_status_must_match_table(
    repo: Path, rows: dict[str, str], statuses: dict[str, str]
) -> None:
    statuses["Grok"] = "working"
    write_state(repo, rows, statuses)
    assert any("grok.md" in e for e in errors(compat.check(repo)))


def test_verified_row_needs_verified_guide(
    repo: Path, rows: dict[str, str], statuses: dict[str, str]
) -> None:
    rows["ChatGPT"] = row(
        "ChatGPT", status="Verified", date="2026-10-15", evidence=EVIDENCE, surface="web app"
    )
    write_state(repo, rows, statuses)
    assert any("chatgpt.md" in e for e in errors(compat.check(repo)))


def test_verified_row_with_evidence_passes(
    repo: Path, rows: dict[str, str], statuses: dict[str, str]
) -> None:
    rows["ChatGPT"] = row(
        "ChatGPT",
        status="Verified",
        date="2026-10-15",
        evidence=EVIDENCE,
        surface="chatgpt.com web, developer-mode connection",
    )
    statuses["ChatGPT"] = "verified"
    write_state(repo, rows, statuses)
    assert errors(compat.check(repo)) == []
