"""The committed repository passes every offline check."""

from __future__ import annotations

from collections.abc import Callable

import pytest

from validation import compat, content, links, schemas, secrets, versions, workflows
from validation.common import REPO_ROOT, Finding

from .conftest import errors

CHECKS: dict[str, Callable[[], list[Finding]]] = {
    "schemas": lambda: schemas.check(REPO_ROOT),
    "versions": lambda: versions.check(REPO_ROOT, ref="refs/heads/main"),
    "content": lambda: content.check(REPO_ROOT),
    "compatibility": lambda: compat.check(REPO_ROOT),
    "links": lambda: links.check(REPO_ROOT),
    "secrets": lambda: secrets.check(REPO_ROOT),
    "workflows": lambda: workflows.check(REPO_ROOT),
}


@pytest.mark.parametrize("name", sorted(CHECKS))
def test_repository_is_clean(name: str) -> None:
    assert errors(CHECKS[name]()) == []
