"""Validators and the whole test suite pass after each documented maintainer step.

Each case edits a repository copy as CONTRIBUTING.md and docs/compatibility.md
describe, then runs ``validate.py all`` and pytest inside that copy. A test that
only passes while the repository is pre-release, unverified or not yet live
fails here.
"""

from __future__ import annotations

import os
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path

import pytest

from .lifecycle import cut_release, launch_service, start_next_cycle, verify_client

NESTED = "REWARDOPEDIA_LIFECYCLE_RUN"

pytestmark = pytest.mark.skipif(
    os.environ.get(NESTED) == "1", reason="already running inside a lifecycle copy"
)


def record_verification(root: Path) -> str:
    verify_client(root, "ChatGPT")
    return "refs/heads/main"


def launch_and_tag_release(root: Path) -> str:
    launch_service(root)
    verify_client(root, "ChatGPT")
    return cut_release(root)


def start_development_after_release(root: Path) -> str:
    launch_and_tag_release(root)
    start_next_cycle(root)
    return "refs/heads/main"


STEPS: dict[str, Callable[[Path], str]] = {
    "client verification recorded": record_verification,
    "service launched and release tagged": launch_and_tag_release,
    "next development cycle": start_development_after_release,
}


def _run(command: list[str], cwd: Path, ref: str) -> subprocess.CompletedProcess[str]:
    env = {**os.environ, NESTED: "1", "GITHUB_REF": ref}
    return subprocess.run(
        command, cwd=cwd, env=env, capture_output=True, text=True, timeout=300, check=False
    )


@pytest.mark.parametrize("step", sorted(STEPS))
def test_suite_passes_after_maintainer_step(repo: Path, tmp_path: Path, step: str) -> None:
    ref = STEPS[step](repo)
    checks = _run([sys.executable, "scripts/validate.py", "all", "--ref", ref], repo, ref)
    assert checks.returncode == 0, checks.stdout + checks.stderr
    suite = _run(
        [
            sys.executable,
            "-m",
            "pytest",
            "-q",
            "-p",
            "no:cacheprovider",
            f"--basetemp={tmp_path / 'nested'}",
        ],
        repo,
        ref,
    )
    assert suite.returncode == 0, suite.stdout[-6000:] + suite.stderr[-2000:]
