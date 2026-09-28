"""Secret and payment-identifier scan for repository files and Git history.

The public package must never contain credentials, tokens, private keys or
payment card numbers. A line can be exempted only with an inline
``secret-scan: allow`` marker, which reviewers must justify.
"""

from __future__ import annotations

import math
import re
import subprocess
from collections.abc import Iterable, Iterator
from pathlib import Path

from .common import Finding, repo_files

CHECK = "secrets"
ALLOW_MARKER = "secret-scan: allow"

PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("private key", re.compile(r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY( BLOCK)?-----")),
    ("AWS access key", re.compile(r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b")),
    ("GitHub token", re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]{36,}|github_pat_[A-Za-z0-9_]{22,})")),
    ("Anthropic key", re.compile(r"\bsk-ant-[A-Za-z0-9_-]{20,}")),
    ("OpenAI key", re.compile(r"\bsk-(?:proj-|svcacct-|admin-)?[A-Za-z0-9_-]{20,}")),
    ("xAI key", re.compile(r"\bxai-[A-Za-z0-9]{20,}")),
    ("Perplexity key", re.compile(r"\bpplx-[A-Za-z0-9]{20,}")),
    ("Slack token", re.compile(r"\bxox[abposr]-[A-Za-z0-9-]{10,}")),
    ("secret or restricted key", re.compile(r"\b[rs]k_(?:live|test)_[A-Za-z0-9]{16,}")),
    ("Google API key", re.compile(r"\bAIza[0-9A-Za-z_-]{35}\b")),
    ("Supabase secret key", re.compile(r"\bsb_secret_[A-Za-z0-9_-]{16,}")),
    (
        "JSON Web Token",
        re.compile(r"\beyJ[A-Za-z0-9_-]{8,}\.eyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}"),
    ),
    (
        "bearer credential",
        re.compile(r"(?i)\bauthorization\b[\"']?\s*[:=]\s*[\"']?bearer\s+[A-Za-z0-9._~+/=-]{16,}"),
    ),
    ("credentials in URL", re.compile(r"\b[a-z][a-z0-9+.-]*://[^/\s:@\"'<>]+:[^/\s@\"'<>]+@")),
)

# A credential-like name, then ':', '=' or a Markdown table cell break, then a
# quoted, code-formatted or unquoted value. The name may be an identifier ending
# in a sensitive word (MCP_SERVICE_KEY, client_secret, export PASSWORD) or
# prose, including Markdown emphasis ("**Client secret:** `...`"). Values stop
# at whitespace, quotes and code punctuation, so calls such as
# os.environ.get(...) are not values.
SENSITIVE_NAME = r"(?:apikey|secret|key|token|password|passwd|pwd|passphrase|credential)s?"
VALUE_CHARS = r"[^\s\"'`<>()\[\]{},;*|]"
ASSIGNMENT = re.compile(
    r"(?i)(?<![A-Za-z0-9])(?:[A-Za-z0-9]+[_. -])*" + SENSITIVE_NAME + r"(?![A-Za-z0-9])"
    r"[\"'*_]{0,3}\s*[:=|]\s*[*_]{0,3}\s*[\"'`]?"
    r"(?P<value>" + VALUE_CHARS + r"{12,})(?!" + VALUE_CHARS + r"|[({])"
)
PLACEHOLDER = re.compile(
    r"(?i)(^<.*>$|\$\{.*\}|^\$[A-Z_]+$|your[_-]|example|placeholder|x{6,}|\*{4,})"
)
# Values that read as words or code references rather than generated
# credentials: "expires-after-an-hour", "IndexNavActive", "process.env.API_TOKEN",
# "STRAPI_TOKEN!".
NOT_A_CREDENTIAL = re.compile(
    r"^(?:(?:[A-Z]?[a-z]+)(?:[-_.]?[A-Z]?[a-z]+)*"
    r"|[A-Za-z_$][\w$]*(?:\.[\w$]+)+!?"
    r"|[A-Z][A-Z0-9]*(?:_[A-Z0-9]+)+!?)$"
)
CARD_CANDIDATE = re.compile(r"(?<![\w.-])(?:\d[ -]?){12,18}\d(?![\w.-])")
SENSITIVE_FILENAMES = re.compile(
    r"(^|/)(\.env(\..*)?|id_[rd]sa|id_ecdsa|id_ed25519|.*\.(pem|key|p12|pfx))$"
)


def shannon_entropy(value: str) -> float:
    counts = {char: value.count(char) for char in set(value)}
    return -sum((n / len(value)) * math.log2(n / len(value)) for n in counts.values())


def luhn_valid(digits: str) -> bool:
    total = 0
    for index, char in enumerate(reversed(digits)):
        digit = int(char)
        if index % 2 == 1:
            digit *= 2
            if digit > 9:
                digit -= 9
        total += digit
    return total % 10 == 0


def scan_line(line: str) -> Iterator[str]:
    """Yield a description for each likely secret on one line."""
    if ALLOW_MARKER in line:
        return
    for label, pattern in PATTERNS:
        if pattern.search(line):
            yield label
    for match in ASSIGNMENT.finditer(line):
        value = match.group("value")
        if (
            not PLACEHOLDER.search(value)
            and not NOT_A_CREDENTIAL.match(value)
            and shannon_entropy(value) >= 3.5
        ):
            yield "hard-coded credential"
    for match in CARD_CANDIDATE.finditer(line):
        digits = re.sub(r"\D", "", match.group(0))
        if 13 <= len(digits) <= 19 and luhn_valid(digits):
            yield "payment card number"


def scan_text(relative: str, lines: Iterable[tuple[int, str]]) -> list[Finding]:
    findings = []
    for number, line in lines:
        for label in scan_line(line):
            findings.append(Finding(CHECK, relative, f"possible {label}", line=number))
    return findings


def scan_files(root: Path) -> list[Finding]:
    findings: list[Finding] = []
    for path in repo_files(root):
        relative = path.as_posix()
        if SENSITIVE_FILENAMES.search(relative):
            findings.append(Finding(CHECK, relative, "credential-like file must not be committed"))
            continue
        try:
            text = (root / path).read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue  # binary assets carry no text secrets we can scan
        findings.extend(scan_text(relative, enumerate(text.splitlines(), start=1)))
    return findings


def scan_history(root: Path) -> list[Finding]:
    """Scan every line added in reachable Git history."""
    try:
        log = subprocess.run(
            ["git", "log", "--all", "-p", "--no-color", "--unified=0", "--format=commit %H"],
            cwd=root,
            check=True,
            capture_output=True,
        ).stdout.decode("utf-8", errors="replace")
    except (OSError, subprocess.CalledProcessError):
        return [Finding(CHECK, ".git", "cannot read Git history", severity="warning")]
    findings: list[Finding] = []
    commit = ""
    current = ""
    for line in log.splitlines():
        if line.startswith("commit "):
            commit = line.split()[1][:12]
        elif line.startswith("+++ "):
            current = line[6:] if line.startswith("+++ b/") else line[4:]
        elif line.startswith("+") and not line.startswith("+++"):
            for label in scan_line(line[1:]):
                findings.append(Finding(CHECK, f"{current}@{commit}", f"possible {label}"))
    return findings


def check(root: Path, history: bool = False) -> list[Finding]:
    findings = scan_files(root)
    if history:
        findings.extend(scan_history(root))
    return findings
