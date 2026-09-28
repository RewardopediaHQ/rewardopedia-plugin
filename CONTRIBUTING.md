# Contributing

Thanks for helping improve the Rewardopedia plugin. This repository holds the
public package only. The MCP server is operated separately, so changes here
cannot alter server behaviour; they change what clients install and what
assistants and users read.

## Ground rules

- **Public, synthetic data only.** Never commit credentials, tokens, real card
  numbers, account identifiers or personal data. Examples use invented cards
  whose identifiers start with `example-` and URLs on reserved example domains.
- **Facts stay honest.** Unknown is never zero or false. Keep units, reward
  currencies, conditions, caps, enrollment, exclusions, effective dates and
  offer restrictions attached. Do not add approval-odds, dollar-savings or
  cross-currency value claims, or declare a universal "best" card.
- **Unverified until tested.** A client or surface becomes `Verified` in
  [docs/compatibility.md](docs/compatibility.md) only with dated, sanitized
  evidence of real tool calls against the deployed service. Documentation,
  handshakes and developer APIs are not evidence.
- **Cite sources.** Client steps and packaging formats must cite official
  documentation in [docs/sources.md](docs/sources.md) with the retrieval date.
- **Provider-neutral skill text.** The skill is loaded by several assistants;
  refer to "the assistant" rather than a specific product.

## Making a change

1. Fork the repository and create a branch.
2. Install tooling: `uv sync --frozen` (requires [uv](https://docs.astral.sh/uv/)).
3. Make one focused change and add a `CHANGELOG.md` entry under
   `## [Unreleased]`.
4. Run the checks:

   ```bash
   uv run python scripts/validate.py all
   uv run pytest
   uv run ruff check . && uv run ruff format --check . && uv run mypy
   ```

5. Open a pull request describing what changed, why, and how you verified it.

CI runs the same checks, an external link check, a full-history secret scan,
actionlint and Claude Code's `claude plugin validate --strict`.

## Versions and releases

- During development every manifest carries the same `X.Y.Z-dev` version.
  CI fails if manifests disagree.
- Only Rewardopedia maintainers cut releases. A release changes every
  manifest to `X.Y.Z`, moves the changelog entries under
  `## [X.Y.Z] - YYYY-MM-DD`, and is tagged `vX.Y.Z` on that commit. CI fails a
  tag that does not match the manifests or that points at a `-dev` version.
- `v0.1.0` waits for the live service and verified client acceptance.

## Updating vendored schemas

Upstream schemas in `schemas/vendor/` are copied unchanged. Follow
[schemas/vendor/README.md](schemas/vendor/README.md) to update them.

## Conduct

Be respectful and constructive. Maintainers may close contributions that add
private data, unverifiable claims or unrelated changes.

By contributing, you agree that your contributions are licensed under the
[MIT License](LICENSE).
