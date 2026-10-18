# Changelog

All notable changes to this package are documented here. The format follows
[Keep a Changelog 1.1.0](https://keepachangelog.com/en/1.1.0/) and versions
follow [Semantic Versioning 2.0.0](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed

- Separate deployed-service status from functional client qualification and stable release.
- Qualify clients independently after shared gates; add Cursor and platform distribution guidance.
- Add public review metadata, existing brand icon, synthetic review cases and release evidence checks.

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

- Backup disclosure (owner decision, monorepo #3544): deletion from
  Rewardopedia is immediate, and provider backup copies roll off automatically
  within about 8 days. The README, privacy guide, tool reference, Spanish
  forget example and `forget_my_context` contract say the same, and retention
  questions or full account deletion go to info@rewardopedia.com. Validation
  rejects a Spanish forget reply that drops that disclosure or says the window
  is unpublished. The contract is re-exported from monorepo `b873973`.
- `recommend_cards` follows the server's `card-qualitative-v2` method
  (monorepo #3545). Recognized but unassessed goals sent beside a supported
  goal are listed in `unassessedGoals` instead of blocking the answer. A stated
  first-year annual-fee waiver passes `maxAnnualFeeUsd` with an
  `annualFeeWaiverNote`. Ties are ordered by comparable always-on rate,
  complementary benefits, then lower known ongoing fee. The skill, tool
  reference and examples are updated, and the tool contract is re-exported
  from monorepo `7fb34f0`.
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
  - `get_earning_rates` does not serve a row whose `effectiveTo` is before
    today's UTC date. A missing `effectiveTo` is an unknown end.
  - Offer `composition`, `search_cards` paging, version conflicts and retries,
    and the `forget_my_context` cascade.
  - Every tool call except `forget_my_context` is recorded in history, and
    recommendation history keeps only the top goal, pair, used saved facts and
    outcome.
- Removed the incorrect claim that saved context accepts free-text notes.
- Client guides rechecked against official documentation on 2026-10-10:
  - ChatGPT uses **Add custom MCP server**, and Rewardopedia grants it the
    OpenID scopes (`openid`, `email` and `profile`; owner decision, monorepo
    #3529). Signing in shares your name, username, avatar and email address
    with ChatGPT. Those identity scopes are not granted to other clients.
  - Claude uses **Use Claude's published identity**.
  - Perplexity uses a public client ID with no secret.
  - Sign-in from Claude Code, Codex, the ChatGPT desktop app and Grok Build is
    not supported for 0.1.0, because only the claude.ai and ChatGPT web OAuth
    clients are pre-registered.
- `docs/sources.md` records a retrieval date per source.

### Not yet included

- Branding (logo and brand colour) awaits owner-supplied assets; see
  [Before v0.1.0](CONTRIBUTING.md#before-v010).
