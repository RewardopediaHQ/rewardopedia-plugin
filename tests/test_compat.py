"""Compatibility claims need evidence; untested surfaces stay unverified."""

from __future__ import annotations

from pathlib import Path

from validation import compat

from .conftest import errors, replace_text

CHATGPT_ROW_STATUS = "| Unverified | not yet verified | none |"


def chatgpt_row(root: Path) -> str:
    text = (root / compat.DOC).read_text(encoding="utf-8")
    return next(line for line in text.splitlines() if line.startswith("| [ChatGPT]"))


def test_verified_without_date_or_evidence_is_rejected(repo: Path) -> None:
    row = chatgpt_row(repo)
    replace_text(
        repo, compat.DOC, row, row.replace(CHATGPT_ROW_STATUS, "| Verified | soon | none |")
    )
    found = errors(compat.check(repo))
    assert any("YYYY-MM-DD" in e for e in found)
    assert any("evidence link" in e for e in found)
    assert any("tested surface" in e for e in found)


def test_unverified_row_cannot_carry_a_date(repo: Path) -> None:
    row = chatgpt_row(repo)
    replace_text(
        repo, compat.DOC, row, row.replace(CHATGPT_ROW_STATUS, "| Unverified | 2026-09-27 | none |")
    )
    assert any("not yet verified" in e for e in errors(compat.check(repo)))


def test_unknown_status_is_rejected(repo: Path) -> None:
    row = chatgpt_row(repo)
    replace_text(
        repo,
        compat.DOC,
        row,
        row.replace(CHATGPT_ROW_STATUS, "| Works | not yet verified | none |"),
    )
    assert any("unknown status" in e for e in errors(compat.check(repo)))


def test_every_consumer_client_needs_a_row(repo: Path) -> None:
    row = chatgpt_row(repo)
    replace_text(repo, compat.DOC, row + "\n", "")
    assert any("missing consumer client row: ChatGPT" in e for e in errors(compat.check(repo)))


def test_guide_status_must_match_table(repo: Path) -> None:
    replace_text(repo, "docs/clients/grok.md", "**Status: unverified.**", "**Status: working.**")
    assert any("grok.md" in e for e in errors(compat.check(repo)))


def test_verified_row_with_evidence_passes(repo: Path) -> None:
    row = chatgpt_row(repo)
    verified = (
        "| [ChatGPT](clients/chatgpt.md) | chatgpt.com web, developer-mode connection | "
        "Pro plan; Rewardopedia account | Verified | 2026-10-15 | "
        "[run 1](https://github.com/RewardopediaHQ/rewardopedia-plugin/issues/1) |"
    )
    replace_text(repo, compat.DOC, row, verified)
    replace_text(
        repo, "docs/clients/chatgpt.md", "**Status: unverified.**", "**Status: verified.**"
    )
    assert errors(compat.check(repo)) == []
