"""A pending sibling cannot block a proven client or stand in for shared acceptance."""

from pathlib import Path

from validation import release

from .conftest import edit_json, errors, write_json
from .lifecycle import current_version, cut_release, verify_client


def accept_backend(root: Path) -> None:
    write_json(
        root,
        release.READINESS,
        {
            "version": current_version(root),
            "sharedBackend": {
                "status": "accepted",
                "verifiedAt": "2026-10-01",
                "serviceCommit": "a" * 40,
                "evidence": ["https://github.com/RewardopediaHQ/rewardopedia-plugin/issues/1"],
            },
        },
    )


def test_one_verified_client_releases_with_siblings_pending(repo: Path) -> None:
    ref = cut_release(repo)
    verify_client(repo, "ChatGPT")
    accept_backend(repo)
    assert errors(release.check(repo, ref)) == []


def test_verified_client_cannot_replace_shared_acceptance(repo: Path) -> None:
    ref = cut_release(repo)
    verify_client(repo, "ChatGPT")
    write_json(repo, release.READINESS, {"sharedBackend": {"status": "pending"}})
    assert any("shared backend" in x for x in errors(release.check(repo, ref)))


def test_shared_acceptance_needs_actual_client_evidence(repo: Path) -> None:
    ref = cut_release(repo)
    accept_backend(repo)
    doc = repo / "docs/compatibility.md"
    text = doc.read_text().replace("| Verified |", "| Unverified |")
    doc.write_text(text)
    assert any("verified surface" in x for x in errors(release.check(repo, ref)))


def test_prior_version_acceptance_cannot_authorize_new_release(repo: Path) -> None:
    ref = cut_release(repo)
    verify_client(repo, "ChatGPT")
    accept_backend(repo)
    edit_json(repo, release.READINESS, lambda data: data.update(version="99.0.0"))
    assert any("shared backend" in x for x in errors(release.check(repo, ref)))


def test_review_metadata_refuses_missing_urls_and_invalid_tools(repo: Path) -> None:
    edit_json(
        repo,
        "plugin.json",
        lambda data: data["extensions"]["com.openai"]["interface"].pop("supportURL"),
    )
    edit_json(
        repo,
        "plugin.json",
        lambda data: data["extensions"]["com.openai"]["review"]["test_cases"]["positive"][0].update(
            tools_triggered="buy_card"
        ),
    )
    found = errors(release.check(repo, "refs/heads/main"))
    assert any("supportURL" in x for x in found)
    assert any("unknown review case tools" in x for x in found)


def test_non_object_manifest_is_reported(repo: Path) -> None:
    write_json(repo, "plugin.json", None)
    found = errors(release.check(repo, "refs/heads/main"))
    assert any("manifest must be a JSON object" in x for x in found)


def test_non_object_nested_values_are_reported(repo: Path) -> None:
    edit_json(repo, "plugin.json", lambda data: data.update(extensions="portable"))
    found = errors(release.check(repo, "refs/heads/main"))
    assert any("extensions must be a JSON object" in x for x in found)
    edit_json(
        repo,
        "plugin.json",
        lambda data: data.update(
            extensions={"com.openai": {"interface": 7, "review": {"test_cases": []}}}
        ),
    )
    found = errors(release.check(repo, "refs/heads/main"))
    assert any("interface must be a JSON object" in x for x in found)
    assert any("review.test_cases must be a JSON object" in x for x in found)
