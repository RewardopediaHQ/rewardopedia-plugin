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

### Not yet included

- Branding (logo, icon and brand colour) awaits owner-supplied assets; see
  [Before v0.1.0](CONTRIBUTING.md#before-v010).
