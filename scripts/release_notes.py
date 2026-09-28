"""Print the CHANGELOG.md section for one release, for the GitHub release notes.

Usage:
    uv run python scripts/release_notes.py 0.1.0

Exit status is 1 when the dated ``## [X.Y.Z] - YYYY-MM-DD`` section is missing
or empty. The release workflow runs this after the version checks pass.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from validation.common import REPO_ROOT
from validation.versions import release_notes


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("version", help="release version without the leading 'v'")
    parser.add_argument("--root", type=Path, default=REPO_ROOT, help="repository root")
    args = parser.parse_args(argv)
    changelog = (args.root / "CHANGELOG.md").read_text(encoding="utf-8")
    try:
        notes = release_notes(changelog, args.version)
    except ValueError as error:
        print(f"ERROR [release-notes] CHANGELOG.md: {error}", file=sys.stderr)
        return 1
    sys.stdout.write(notes)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
