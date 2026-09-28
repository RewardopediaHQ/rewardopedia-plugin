"""Internal and external link checks for Markdown and manifest URLs.

Internal links (relative paths and ``#anchors``) must resolve. External URLs
must use HTTPS. With ``external=True`` each unique external URL is also
requested: 404/410 and connection failures are errors, while responses that
cannot confirm a page (401, 403, 429, 5xx, timeouts) from bot-protected hosts
are warnings.
"""

from __future__ import annotations

import json
import re
import time
import unicodedata
import urllib.error
import urllib.request
from collections.abc import Iterator
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlsplit

from .common import Finding, repo_files
from .constants import NOT_YET_LIVE_HOSTS, REPOSITORY_URL

CHECK = "links"

INLINE_LINK = re.compile(
    r"(?<!!)\[(?:[^\[\]]|\[[^\]]*\])*\]\(\s*<?([^)\s>]+)>?(?:\s+\"[^\"]*\")?\s*\)"
)
IMAGE_LINK = re.compile(r"!\[[^\]]*\]\(\s*<?([^)\s>]+)>?(?:\s+\"[^\"]*\")?\s*\)")
REFERENCE_DEF = re.compile(r"^\s{0,3}\[[^\]]+\]:\s*<?(\S+?)>?(?:\s+\"[^\"]*\")?\s*$")
AUTOLINK = re.compile(r"<(https?://[^>\s]+)>")
HEADING = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
FENCE = re.compile(r"^\s*(```|~~~)")
INLINE_CODE = re.compile(r"`[^`]*`")
URL_KEYS = frozenset(
    {"homepage", "repository", "url", "websiteURL", "privacyPolicyURL", "termsOfServiceURL"}
)
RESERVED_EXAMPLE_HOSTS = ("example", "example.com", "example.net", "example.org")
UNCONFIRMABLE_STATUSES = frozenset({401, 403, 405, 429, 500, 502, 503, 504})
USER_AGENT = (
    "rewardopedia-plugin-link-check/1.0 (+https://github.com/RewardopediaHQ/rewardopedia-plugin)"
)


def github_slug(text: str) -> str:
    """Approximate GitHub's heading anchor algorithm."""
    text = re.sub(r"`([^`]*)`", r"\1", text)
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)
    slug = []
    for char in text.strip().lower():
        category = unicodedata.category(char)
        if char in {" ", "-"}:
            slug.append("-")
        elif char == "_" or category[0] in {"L", "N"}:
            slug.append(char)
    return "".join(slug)


def markdown_lines(text: str) -> Iterator[tuple[int, str]]:
    """Yield ``(line_number, line)`` for lines outside fenced code blocks."""
    in_fence = False
    for number, line in enumerate(text.splitlines(), start=1):
        if FENCE.match(line):
            in_fence = not in_fence
            continue
        if not in_fence:
            yield number, line


def anchors(text: str) -> set[str]:
    seen: dict[str, int] = {}
    result = set()
    for _, line in markdown_lines(text):
        match = HEADING.match(line)
        if not match:
            continue
        slug = github_slug(match.group(2))
        count = seen.get(slug, 0)
        seen[slug] = count + 1
        result.add(slug if count == 0 else f"{slug}-{count}")
    return result


def markdown_targets(text: str) -> Iterator[tuple[int, str]]:
    """Yield ``(line_number, target)`` for links outside code spans and blocks."""
    for number, raw in markdown_lines(text):
        line = INLINE_CODE.sub("", raw)
        for pattern in (INLINE_LINK, IMAGE_LINK, AUTOLINK):
            for match in pattern.finditer(line):
                yield number, match.group(1)
        reference = REFERENCE_DEF.match(line)
        if reference:
            yield number, reference.group(1)


def json_urls(data: Any) -> Iterator[str]:
    if isinstance(data, dict):
        for key, value in data.items():
            if key in URL_KEYS and isinstance(value, str):
                yield value
            else:
                yield from json_urls(value)
    elif isinstance(data, list):
        for item in data:
            yield from json_urls(item)


def is_reserved_example(host: str) -> bool:
    return any(host == h or host.endswith("." + h) for h in RESERVED_EXAMPLE_HOSTS)


def _check_internal(
    root: Path, source: Path, number: int, target: str, cache: dict[Path, set[str]]
) -> list[Finding]:
    relative = source.as_posix()
    path_part, _, fragment = target.partition("#")
    if path_part:
        resolved = (root / source.parent / unquote(path_part)).resolve()
        try:
            resolved.relative_to(root.resolve())
        except ValueError:
            return [Finding(CHECK, relative, f"link escapes the repository: {target}", line=number)]
        if not resolved.exists():
            return [Finding(CHECK, relative, f"broken relative link: {target}", line=number)]
    else:
        resolved = (root / source).resolve()
    if fragment and resolved.is_file() and resolved.suffix == ".md":
        if resolved not in cache:
            cache[resolved] = anchors(resolved.read_text(encoding="utf-8"))
        if fragment.lower() not in cache[resolved]:
            return [Finding(CHECK, relative, f"missing anchor: {target}", line=number)]
    return []


def collect(root: Path) -> tuple[dict[str, list[tuple[str, int | None]]], list[Finding]]:
    """Check internal links; return external URLs mapped to their locations."""
    findings: list[Finding] = []
    external: dict[str, list[tuple[str, int | None]]] = {}
    cache: dict[Path, set[str]] = {}
    for path in repo_files(root):
        relative = path.as_posix()
        if path.suffix == ".md":
            text = (root / path).read_text(encoding="utf-8")
            for number, target in markdown_targets(text):
                scheme = urlsplit(target).scheme
                if scheme in {"http", "https"}:
                    external.setdefault(target, []).append((relative, number))
                elif scheme == "mailto":
                    continue
                elif scheme:
                    findings.append(
                        Finding(CHECK, relative, f"unsupported link scheme: {target}", line=number)
                    )
                else:
                    findings.extend(_check_internal(root, path, number, target, cache))
        elif path.suffix == ".json" and path.parts[0] not in {"schemas", "examples"}:
            try:
                data = json.loads((root / path).read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                continue  # reported by the schema check
            for url in json_urls(data):
                external.setdefault(url, []).append((relative, None))
    for url, locations in external.items():
        if urlsplit(url).scheme != "https":
            for location, line in locations:
                findings.append(Finding(CHECK, location, f"use https: {url}", line=line))
    return external, findings


def _request(url: str, method: str, timeout: float) -> int:
    request = urllib.request.Request(url, method=method, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return int(response.status)
    except urllib.error.HTTPError as error:
        return int(error.code)


def probe(url: str, timeout: float = 20.0, attempts: int = 2) -> tuple[int | None, str | None]:
    """Return ``(status, error)`` for an external URL, trying HEAD then GET."""
    last_error: str | None = None
    for attempt in range(attempts):
        try:
            status = _request(url, "HEAD", timeout)
            if status in {403, 404, 405, 501} or status >= 500:
                status = _request(url, "GET", timeout)
            if status < 500 or attempt == attempts - 1:
                return status, None
        except (urllib.error.URLError, TimeoutError, OSError) as error:
            last_error = str(getattr(error, "reason", error))
        time.sleep(1.5 * (attempt + 1))
    return None, last_error


def check_external(external: dict[str, list[tuple[str, int | None]]]) -> list[Finding]:
    findings: list[Finding] = []
    for url in sorted(external):
        host = urlsplit(url).hostname or ""
        if host in NOT_YET_LIVE_HOSTS or is_reserved_example(host):
            continue
        if url == REPOSITORY_URL or url.startswith(REPOSITORY_URL + "/"):
            continue  # this repository; internal links are checked separately
        status, error = probe(url)
        relative, number = external[url][0]
        if status is None:
            timed_out = error is not None and "timed out" in error.lower()
            findings.append(
                Finding(
                    CHECK,
                    relative,
                    f"could not reach {url}: {error}",
                    severity="warning" if timed_out else "error",
                    line=number,
                )
            )
        elif status in UNCONFIRMABLE_STATUSES:
            findings.append(
                Finding(
                    CHECK,
                    relative,
                    f"HTTP {status} for {url}; host may block automated checks",
                    severity="warning",
                    line=number,
                )
            )
        elif status >= 400:
            findings.append(Finding(CHECK, relative, f"HTTP {status} for {url}", line=number))
    return findings


def check(root: Path, external: bool = False) -> list[Finding]:
    urls, findings = collect(root)
    if external:
        findings.extend(check_external(urls))
    return findings
