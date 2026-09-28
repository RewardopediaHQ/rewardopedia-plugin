# Client compatibility

A client is **Verified** only after a real, signed-in Rewardopedia account
completes actual tool calls on the listed surface against the deployed
service, with the build and package version recorded as evidence. Protocol
handshakes, API-only calls, developer surfaces and documentation are not
verification. Every other surface is **Unverified**.

The Rewardopedia MCP server (`https://mcp.rewardopedia.com/mcp`) is not live
yet, so no surface has been verified.

## Consumer surfaces

| Client | Tested surface | Account prerequisites | Status | Verification date | Evidence |
| --- | --- | --- | --- | --- | --- |
| [ChatGPT](clients/chatgpt.md) | none yet (target: chatgpt.com web, developer-mode MCP connection) | Plan and workspace policy that allow developer mode; OpenAI documents read/fetch-only MCP for Pro and full MCP for Business, Enterprise and Edu; Rewardopedia account | Unverified | not yet verified | none |
| [Claude](clients/claude.md) | none yet (target: claude.ai custom connector) | Free (one custom connector), Pro, Max, Team or Enterprise; Team and Enterprise need an Owner to add it; Rewardopedia account | Unverified | not yet verified | none |
| [Grok](clients/grok.md) | none yet (target: grok.com custom MCP connector) | Grok account; Business and Enterprise need admin provisioning; OAuth client values pending; Rewardopedia account | Unverified | not yet verified | none |
| [Perplexity](clients/perplexity.md) | none yet (target: perplexity.ai custom remote connector) | Pro, Max or Enterprise; OAuth client values pending; Rewardopedia account | Unverified | not yet verified | none |

## Developer surfaces

These package formats are validated in CI. On 2026-09-27 a local installation
from a checkout loaded the skill and the `rewardopedia` MCP server entry in
Claude Code 2.1.283, and Codex CLI 0.156.1 installed the plugin and listed the
server entry. No tool has been called against a live server, so every row
stays unverified. Developer surfaces never count
toward consumer verification.

| Client | Tested surface | Account prerequisites | Status | Verification date | Evidence |
| --- | --- | --- | --- | --- | --- |
| [Claude Code](clients/claude.md#developer-surface-claude-code) | none yet (target: plugin from this repository's marketplace) | Claude Code; Rewardopedia account | Unverified | not yet verified | none |
| [Codex and ChatGPT desktop](clients/chatgpt.md#developer-surface-codex-and-the-chatgpt-desktop-app) | none yet (target: portable plugin from a local or repository marketplace) | Codex or the ChatGPT desktop app; Rewardopedia account | Unverified | not yet verified | none |
| [Grok Build](clients/grok.md#developer-surface-grok-build) | none yet (target: Claude Code-compatible plugin) | Grok Build; Rewardopedia account | Unverified | not yet verified | none |

## Recording a verification

When a surface is verified, change its row in the same pull request that adds
the evidence:

- **Tested surface:** the exact surface and app version, if shown.
- **Status:** `Verified`.
- **Verification date:** the ISO date of the test run (`YYYY-MM-DD`).
- **Evidence:** a link to sanitized evidence that records the deployed build,
  package version, account prerequisite and the successful tool calls. Never
  include tokens, account identifiers or personal data.

CI rejects a `Verified` row without an ISO date and an evidence link, and any
other row whose verification date is not `not yet verified`.
