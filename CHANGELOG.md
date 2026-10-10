# Changelog

All notable changes to this package are documented here. The format follows
[Keep a Changelog 1.1.0](https://keepachangelog.com/en/1.1.0/) and versions
follow [Semantic Versioning 2.0.0](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Portable Agent Plugins manifest (`plugin.json`, `mcp.json`) with OpenAI
  install-surface metadata, and Claude Code manifest, marketplace and
  `.mcp.json`, all pointing at `https://mcp.rewardopedia.com/mcp` (not yet live).
- `card-recommendations` skill and reference for the eleven MCP tools. The skill
  gives the request-history notice before the first Rewardopedia call, and
  treats the returned candidate order as a methodology order, not a verdict.
- Privacy, memory, retention and deletion guide. It explains that request
  history is recorded automatically for every tool request, including
  searches and comparisons.
- Unverified setup guides for ChatGPT, Claude, Grok and Perplexity, and a
  compatibility table.
- Synthetic example conversations, including tied candidates presented without
  a "best" pick.
- Validation for schemas, version consistency, links, secrets, compatibility
  claims and workflow hygiene, runnable locally and in CI. It checks that
  every guide and manifest uses the canonical endpoint, and its secret scan
  covers unquoted, YAML and prose credentials.
- Release workflow: a `vX.Y.Z` tag reruns every check, then publishes a GitHub
  release with the changelog section, versioned archives and `SHA256SUMS`.
- Lifecycle tests that rerun the suite after a recorded verification, a
  service launch, a release tag and the next development cycle.
- The server's tool contract (names, descriptions, annotations, input schemas
  and output field names), exported from Rewardopedia's server code into
  `schemas/vendor/rewardopedia-mcp/tools.json` with a pinned hash. The schema
  check validates every example's tool-call arguments against it, with no
  invented arguments allowed, and rejects result fields a tool does not
  return.

### Changed

- Resynchronised the skill, tool reference, privacy guide and examples with
  the server's current contract:
  - `recommend_cards` needs `cards:read` and `context:read` only, accepts no
    context updates and reads saved context itself.
  - Real argument names (`contentLocale`, `slugs`, `constraints`, `requestId`,
    `expectedVersion`, `updates`, `removeIds`, `all`, `entryIds`,
    `requestIds`) and result shapes.
  - `compare_cards` takes 2 to 5 cards and reports `duplicate` entries and
    `complete`.
  - `get_card_fees` serves annual and foreign transaction fees and lists the
    rest in `unreportedFeeTypes`; `waivedFirstYear` appears only when the
    source states it.
  - Offer `composition`, `search_cards` paging, version conflicts and retries,
    and the `forget_my_context` cascade.
  - Every tool call except `forget_my_context` is recorded in history, and
    recommendation history keeps only the top goal, pair, used saved facts and
    outcome.
- Removed the incorrect claim that saved context accepts free-text notes.
- Client guides rechecked against official documentation on 2026-10-10:
  - ChatGPT uses **Add custom MCP server**; its OpenID scope request is an open
    owner decision.
  - Claude uses **Use Claude's published identity**.
  - Perplexity uses a public client ID with no secret.
  - Sign-in from Claude Code, Codex, the ChatGPT desktop app and Grok Build is
    not supported for 0.1.0, because only the claude.ai and ChatGPT web OAuth
    clients are pre-registered.
- `docs/sources.md` records a retrieval date per source.

### Not yet included

- Branding (logo, icon and brand colour) awaits owner-supplied assets; see
  [Before v0.1.0](CONTRIBUTING.md#before-v010).
