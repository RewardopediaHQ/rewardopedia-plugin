# Client compatibility

A client is **Verified** only after a real, signed-in Rewardopedia account
completes actual tool calls on the listed surface against the deployed
service, with the build and package version recorded as evidence. Protocol
handshakes, API-only calls, package loading and documentation are not
verification. Every other surface is **Unverified**.

The service is deployed; `/ready` returned 200 with eleven tools on 2026-10-18.
This proves reachability, not any client's functional acceptance. Shared backend
gates plus the first independently verified surface can release; other clients
remain open. A client-specific OAuth or directory delay does not block a
qualified sibling. Prerequisite claims below require recheck at execution;
packaging/publication routes were rechecked on 2026-10-18. ChatGPT connection
steps and Codex MCP/OAuth guidance were rechecked on 2026-10-19; the current
ChatGPT Plugins flow requires no Developer Mode toggle.

## Consumer surfaces

| Client | Tested surface | Account prerequisites | Status | Verification date | Evidence |
| --- | --- | --- | --- | --- | --- |
| [ChatGPT](clients/chatgpt.md) | none yet (target: chatgpt.com web, custom MCP server from Plugins) | Workspace permission to create plugins with MCPs; OpenAI documents read/fetch-only MCP for Pro and full MCP for Business, Enterprise and Edu; ChatGPT receives the OpenID scopes (name, username, avatar and email); Rewardopedia account | Unverified | not yet verified | none |
| [Claude](clients/claude.md) | none yet (target: claude.ai custom connector using Claude's published identity) | Free (one custom connector), Pro, Max, Team or Enterprise; Team and Enterprise need an Owner to add it; Rewardopedia account | Unverified | not yet verified | none |
| [Grok](clients/grok.md) | none yet (target: grok.com custom MCP connector) | Grok account; Business and Enterprise need admin provisioning; OAuth client registration pending; Rewardopedia account | Unverified | not yet verified | none |
| [Perplexity](clients/perplexity.md) | none yet (target: perplexity.ai custom remote connector) | Pro, Max or Enterprise; public OAuth client ID pending (no secret); Rewardopedia account | Unverified | not yet verified | none |

## Developer surfaces

These package formats are validated in CI. On 2026-09-27 a local installation
from a checkout loaded the skill and the `rewardopedia` MCP server entry in
Claude Code 2.1.283, and Codex CLI 0.156.1 installed the plugin and listed the
server entry. Each developer surface needs its own approved OAuth registration
and complete functional acceptance. Package loading alone does not qualify any
surface. A verified developer surface can release independently of the web client.

| Client | Tested surface | Account prerequisites | Status | Verification date | Evidence |
| --- | --- | --- | --- | --- | --- |
| [Claude Code](clients/claude.md#developer-surface-claude-code) | none yet (target: plugin from this repository's marketplace) | Claude Code; Rewardopedia account; OAuth prerequisites and functional acceptance pending | Unverified | not yet verified | none |
| [Codex](clients/chatgpt.md#developer-surface-codex-and-the-chatgpt-desktop-app) | none yet (target: portable plugin from a local or repository marketplace) | Codex; Rewardopedia account; OAuth prerequisites and functional acceptance pending | Unverified | not yet verified | none |
| [ChatGPT desktop](clients/chatgpt.md#developer-surface-codex-and-the-chatgpt-desktop-app) | none yet (target: portable plugin from a local or repository marketplace) | ChatGPT desktop; Rewardopedia account; OAuth prerequisites and functional acceptance pending | Unverified | not yet verified | none |
| [Grok Build](clients/grok.md#developer-surface-grok-build) | none yet (target: Claude Code-compatible plugin) | Grok Build; Rewardopedia account; OAuth prerequisites and functional acceptance pending | Unverified | not yet verified | none |
| [Cursor](clients/cursor.md) | none yet (target: portable Agent Plugin) | Cursor account and plugin support; approved OAuth registration; Rewardopedia account | Unverified | not yet verified | none |

## Recording a verification

When a surface is verified, change its row in the same pull request that adds
the evidence:

- **Tested surface:** the exact surface and app version, if shown.
- **Status:** `Verified`.
- **Verification date:** the ISO date of the test run (`YYYY-MM-DD`).
- **Evidence:** a link to sanitized evidence that records the deployed build,
  package version, account prerequisite and the successful tool calls in both
  US languages. Include context correction/deletion, two-account isolation,
  source/date links and relevant refusal/reconnect/outage behavior. Never
  include tokens, account identifiers or personal data.

CI rejects a `Verified` row without an ISO date and an evidence link, and any
other row whose verification date is not `not yet verified`.
