# Rewardopedia plugin

> [!WARNING]
> **NOT YET LIVE.** The Rewardopedia MCP server at
> `https://mcp.rewardopedia.com/mcp` has not launched. Nothing in this
> repository works yet, no client has been verified, and nothing has been
> released. The package version is `0.1.0-dev`.

This repository is the public, MIT-licensed package that connects AI
assistants to Rewardopedia's remote MCP server at
`https://mcp.rewardopedia.com/mcp`. It lets an assistant search and
compare US credit cards using published, source-referenced facts, and build a
qualitative shortlist for a goal you choose, optionally using facts saved to
your Rewardopedia account.

It contains manifests, an assistant skill, client setup guides, synthetic
examples and validation. It contains no server code and no customer data.

## What it will do

The server exposes eleven tools, documented in the
[tool reference](skills/card-recommendations/references/tools.md):

| Area | Tools |
| --- | --- |
| Card facts | `search_cards`, `get_card_detail`, `compare_cards`, `get_card_offers`, `get_card_benefits`, `get_earning_rates`, `get_card_fees` |
| Recommendations | `recommend_cards` |
| Your saved context | `get_my_context`, `update_my_context`, `forget_my_context` |

Scope and limits:

- US market only, in English (`en-US`) and Spanish (`es-US`). Other markets are
  refused rather than substituted.
- Shortlists are qualitative: three candidates by default, at most five, each
  with reasons, conditions, limitations and sources.
- Unknown facts stay unknown; they are never treated as zero or "none".
- No approval odds, eligibility decisions, dollar-savings estimates or
  comparisons that treat different reward currencies as equal money.

## Before you use it: privacy and memory

Rewardopedia keeps two kinds of data in your Rewardopedia account:

- **Facts you state explicitly:** cards you say you hold, spending, goals,
  preferences, constraints and temporary plans. Your assistant saves these when
  you state them. Rewardopedia's instructions tell it to explain what is saved
  first and not to save anything you ask it not to. Searches, comparisons and
  hypothetical questions never become facts.
- **A sanitized history of every Rewardopedia tool request.** This is recorded
  automatically, even if you never save a fact. It includes card searches and
  comparisons.

Both belong to your Rewardopedia account and are shared by every assistant you
connect with that account.

- Never share card numbers, security codes, account numbers, government
  identifiers, passwords or other credentials.
- Saved facts and request history are kept until you delete them or your
  account.
- Ask your assistant what Rewardopedia remembers at any time, and ask it to
  forget some or all of it. Deletion is permanent in the live service; backup
  retention limits will be published before release.

Read the full [privacy, memory, retention and deletion guide](docs/privacy-and-memory.md)
before connecting.

## Permissions

Signing in uses OAuth with your Rewardopedia account. No API key or secret is
stored in this package.

| Permission | What it allows |
| --- | --- |
| `cards:read` | Search, look up and compare published card facts |
| `context:read` | Read your saved context and history, and use it for recommendations |
| `context:write` | Save, correct and delete your saved context |

## Connect an assistant

All guides are **unverified** until each client passes a live test; see the
[compatibility table](docs/compatibility.md).

| Client | Guide | Status |
| --- | --- | --- |
| ChatGPT | [ChatGPT setup](docs/clients/chatgpt.md) | Unverified |
| Claude | [Claude setup](docs/clients/claude.md) | Unverified |
| Grok | [Grok setup](docs/clients/grok.md) | Unverified |
| Perplexity | [Perplexity setup](docs/clients/perplexity.md) | Unverified |

The packaging formats and client steps are based on official documentation
listed in [docs/sources.md](docs/sources.md).

## Package layout

| Path | Purpose |
| --- | --- |
| `plugin.json`, `mcp.json` | Portable [Agent Plugins 1.0.0](https://agent-plugins.org/) manifest and remote MCP server, with OpenAI install-surface metadata |
| `.claude-plugin/plugin.json`, `.mcp.json` | Claude Code plugin manifest and remote MCP server |
| `.claude-plugin/marketplace.json` | Claude Code marketplace that serves this repository as one plugin |
| `skills/card-recommendations/` | Assistant skill and the eleven-tool reference |
| `docs/` | Privacy guide, client guides, compatibility table and sources |
| `examples/` | Synthetic example conversations |
| `schemas/`, `validation/`, `scripts/`, `tests/` | Validation used locally and in CI |
| `.github/workflows/` | CI validation, and the release workflow that publishes a tagged version |

## Validate locally

Requires [uv](https://docs.astral.sh/uv/) and Python 3.12.

```bash
uv sync --frozen
uv run python scripts/validate.py all        # schemas, versions, content, compatibility, links, secrets, workflows
uv run python scripts/validate.py links --external
uv run python scripts/validate.py secrets --history
uv run pytest
uv run ruff check . && uv run ruff format --check . && uv run mypy
```

With Node.js 24 you can also run Claude Code's own validator:

```bash
npx --yes @anthropic-ai/claude-code@2.1.283 plugin validate --strict .
npx --yes @anthropic-ai/claude-code@2.1.283 plugin validate --strict .claude-plugin/plugin.json
```

## Contributing, security and license

- [Contributing](CONTRIBUTING.md)
- [Security policy](SECURITY.md)
- [Changelog](CHANGELOG.md)
- [MIT License](LICENSE)
