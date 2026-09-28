"""The secret scan finds credentials and card numbers without flagging placeholders.

Fake secrets are assembled at runtime so this file never contains one literally.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from validation import secrets

from .conftest import errors

FAKE = {
    "private key": "-----BEGIN " + "RSA PRIVATE KEY-----",
    "AWS access key": "AKIA" + "ABCDEFGHIJKLMNOP",
    "GitHub token": "ghp_" + "a1B2c3D4e5F6g7H8i9J0k1L2m3N4o5P6q7R8",
    "Anthropic key": "sk-ant-" + "api03-abcdefghijklmnopqrstuvwxyz",
    "OpenAI key": "sk-proj-" + "abcdefghijklmnopqrstuvwxyz0123",
    "xAI key": "xai-" + "abcdefghijklmnopqrstuvwxyz",
    "Perplexity key": "pplx-" + "abcdefghijklmnopqrstuvwxyz",
    "Slack token": "xoxb-" + "123456789012-abcdefghij",
    "secret or restricted key": "sk_" + "live_" + "abcdefghijklmnopqrstuv",
    "Google API key": "AIza" + "SyA1234567890abcdefghijklmnopqrstuv",
    "Supabase secret key": "sb_" + "secret_" + "abcdefghijklmnop0123456789",
    "JSON Web Token": "eyJ" + "hbGciOiJIUzI1NiJ9." + "eyJ" + "zdWIiOiIxMjM0NTYifQ.abcdefghijklmnop",
    "bearer credential": "Authorization: " + "Bearer abcdefghijklmnopqrstuvwxyz012345",
    "credentials in URL": "https://user:" + "p4ssw0rd@example.com/path",
    "hard-coded credential": 'client_secret = "' + "Zx9Qw3Er7Ty1Ui5Op2As" + '"',
    "payment card number": "4111 1111 " + "1111 1111",
}


@pytest.mark.parametrize("label", sorted(FAKE))
def test_detects_secret(label: str) -> None:
    assert label in set(secrets.scan_line(f"value: {FAKE[label]}"))


# A random-looking value; assembled so this file never holds a literal secret.
VALUE = "Zx9Qw3Er7Ty1" + "Ui5Op2AsDf8Gh4Jk6Lz0"


@pytest.mark.parametrize(
    "line",
    [
        "MCP_SERVICE_KEY=" + VALUE,
        "export PASSWORD=" + VALUE,
        "client_secret=" + VALUE,
        "  token: " + VALUE,
        "      MCP_ACTOR_SIGNING_KEY: " + VALUE,
        '"client_secret": "' + VALUE + '",',
        "SUPABASE_KEY=" + VALUE,
        "Client secret: " + VALUE,
        "- **Client secret:** `" + VALUE + "`",
        "| Client secret | `" + VALUE + "` |",
        "APIKEY='" + VALUE + "'",
    ],
)
def test_detects_unquoted_and_prose_credentials(line: str) -> None:
    assert "hard-coded credential" in set(secrets.scan_line(line))


@pytest.mark.parametrize(
    "line",
    [
        'client_secret = "<your-client-secret>"',
        "GH_TOKEN: ${{ github.token }}",
        "key: tsbuildinfo-${{ runner.os }}-${{ hashFiles('uv.lock') }}",
        "token = os.environ.get('GITHUB_TOKEN')",
        "const TOKEN = process.env.REWARDOPEDIA_API_TOKEN;",
        "password=$DB_PASSWORD",
        "The access token: expires-after-an-hour",
        "| Token | Opaque-and-verified-on-every-request |",
        "{ key: IndexNavActive; label: string }",
        "sorted(findings, key=lambda e: list(e.absolute_path))",
        "keywords: credit-cards",
        'api_key: "${REWARDOPEDIA_API_KEY}"',
        'password = "example-password-value"',
        "Order number 1234 5678 9012 3456 is not a card",  # fails the Luhn check
        "sha256 0a4aad95ce337878ad38802ebf0daa3fde76abe3f65400c86bcbb1ec0b3ab883",
        "Retrieved on 2026-09-27; 100 requests per minute and 1,000 per hour.",
    ],
)
def test_ignores_non_secrets(line: str) -> None:
    assert list(secrets.scan_line(line)) == []


@pytest.mark.parametrize(
    "line",
    [
        "password = readVault2Secret(name)",
        "token = os.environ.get('GITHUB_TOKEN')",
        "key: tsbuildinfo-${{ runner.os }}",
    ],
)
def test_calls_and_template_expressions_are_not_values(line: str) -> None:
    assert secrets.ASSIGNMENT.search(line) is None


def test_allow_marker_exempts_a_line() -> None:
    line = f"{FAKE['AWS access key']}  # {secrets.ALLOW_MARKER} documented test vector"
    assert list(secrets.scan_line(line)) == []


def test_luhn() -> None:
    valid = "4" + "1" * 15
    assert secrets.luhn_valid(valid)
    assert not secrets.luhn_valid(valid[:-1] + "2")


def test_file_scan_reports_line(repo: Path) -> None:
    with (repo / "docs/sources.md").open("a", encoding="utf-8") as handle:
        handle.write(f"\n{FAKE['GitHub token']}\n")
    found = errors(secrets.check(repo))
    assert any("docs/sources.md:" in e and "GitHub token" in e for e in found)


def test_credential_files_are_rejected(repo: Path) -> None:
    (repo / ".env").write_text("NOTHING=1\n", encoding="utf-8")
    (repo / "deploy.pem").write_text("placeholder\n", encoding="utf-8")
    found = errors(secrets.check(repo))
    assert any(".env" in e for e in found) and any("deploy.pem" in e for e in found)


def _git(root: Path, *args: str) -> None:
    subprocess.run(
        ["git", "-c", "user.name=Test", "-c", "user.email=test@example.com", *args],
        cwd=root,
        check=True,
        capture_output=True,
    )


def test_history_scan_finds_removed_secret(tmp_path: Path) -> None:
    _git(tmp_path, "init", "-q", "-b", "main")
    leaked = tmp_path / "notes.md"
    leaked.write_text(f"token {FAKE['Slack token']}\n", encoding="utf-8")
    _git(tmp_path, "add", "notes.md")
    _git(tmp_path, "commit", "-q", "-m", "add notes")
    leaked.write_text("clean\n", encoding="utf-8")
    _git(tmp_path, "commit", "-q", "-am", "remove token")
    assert errors(secrets.check(tmp_path)) == []
    history = errors(secrets.check(tmp_path, history=True))
    assert any("notes.md@" in e and "Slack token" in e for e in history)
