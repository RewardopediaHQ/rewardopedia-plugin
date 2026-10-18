# Distribution packet

Prepared 2026-10-18. All targets are **not submitted**; client functional
qualification remains unverified. This packet is review material, not evidence
of a listing, backlink or successful installation.

## Shared package

- Name / publisher: Rewardopedia.
- Public source: https://github.com/RewardopediaHQ/rewardopedia-plugin
- Current package: `0.1.0-dev`; replace with the qualified stable tag and archive
  checksums before submission. Do not submit a development version as stable.
- Product: https://www.rewardopedia.com
- Support: https://www.rewardopedia.com/contact
- Privacy: https://www.rewardopedia.com/policy
- Terms: https://www.rewardopedia.com/terms
- Remote MCP: `https://mcp.rewardopedia.com/mcp` (HTTP transport, OAuth).
- Scope: US credit-card facts and qualitative matching in en-US and es-US;
  eleven tools, optional saved context and automatic sanitized request history.
  No live booking, approval guarantee, financial transaction or travel-data claim.
- Assets and review cases: `plugin.json`, `assets/rewardopedia-icon.png`.
- Qualification: [compatibility](compatibility.md), `release-readiness.json`.
- Example: search for dining cards, compare returned canonical identities, then
  request a Spanish US shortlist. Preserve the returned sources, dates,
  conditions and relevant Rewardopedia page links. Synthetic response examples
  live in `examples/`; they are not production acceptance evidence.

## Target packets and remaining prerequisites

| Target | Official route | Remaining prerequisite |
| --- | --- | --- |
| ChatGPT / Codex | [OpenAI submission](https://developers.openai.com/plugins/deploy/submission) | Qualify each surface's OAuth/install/tool flow; attach a real demo recording and provide reviewer access only through the secure dashboard. ZIP contains five positive and three negative review plans, not completed results. |
| Claude / Claude Code | [Claude submission portal](https://claude.com/resources/articles/build-plugins-for-claude) | Separate web connector and Code plugin OAuth/functional evidence. Validate the bundled marketplace and install the exact release. |
| Cursor | [Portable plugin reference](https://cursor.com/docs/reference/plugins) | Validate the portable manifest, OAuth prerequisites and a fresh IDE installation before marketplace submission. |
| Grok web | [Custom connectors](https://docs.x.ai/grok/connectors) | Verify account tier, registration and real tool flow; no public catalog route is claimed. |
| Grok Build | [Plugins and marketplace sources](https://docs.x.ai/build/features/skills-plugins-marketplaces) | Qualify source installation and OAuth separately from any central catalog placement. |
| Perplexity | [Remote MCP guidance](https://www.perplexity.ai/help-center/en/articles/11502712-local-and-remote-mcps-for-perplexity) | Verify supported account/surface and public OAuth registration; client values are still pending. |
| Official MCP Registry | [Publisher guide](https://modelcontextprotocol.io/registry/quickstart) | Verify namespace/domain ownership and current remote-server schema. Prepare versioned metadata against the qualified HTTPS endpoint; validate with the current publisher before authorized publication. |
| Smithery | [Publish guide](https://smithery.ai/docs/build/publish) | Verify current remote-server ownership/claim and OAuth support, then validate this metadata and the actual installation path. |
| Glama | [Server directory](https://glama.ai/mcp/servers) | Verify the current listing/claim route and remote OAuth install support before filing the packet. |

Record package validation, direct connection, functional qualification,
submission, approval, listing availability and successful installation as
separate dated states. Keep the listing URL, link destination/attributes and
actual referral evidence. Compare successful connections, useful tool calls,
referral visits and organic-search results over comparable windows. A submission
does not establish a backlink, and a listing does not guarantee ranking gains.

Platform documentation can change; recheck it immediately before execution.
Publication and reviewer-account provisioning retain their specific approvals.
