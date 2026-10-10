# Packaging and client sources

Every packaging format and client setup step in this repository is based on the
official documentation below. Each row gives the date the page was last read.
Client products change often: recheck each source before verifying a client or
cutting a release, and update its date when you do.

## Portable package (Agent Plugins and Agent Skills)

| Topic | Source | Retrieved | What this repository uses |
| --- | --- | --- | --- |
| Agent Plugins 1.0.0 overview | [agent-plugins.org](https://agent-plugins.org/) | 2026-09-27 | Root `plugin.json`, root `mcp.json`, `skills/` layout |
| Plugin manifest schema | [plugin.schema.json](https://agent-plugins.org/schemas/1.0.0/plugin.schema.json) | 2026-09-27 | Vendored copy in `schemas/vendor/agent-plugins-1.0.0/` |
| MCP configuration schema | [mcp.schema.json](https://agent-plugins.org/schemas/1.0.0/mcp.schema.json) | 2026-09-27 | Vendored copy; `streamable-http` transport |
| Agent Skills format | [agentskills.io/specification](https://agentskills.io/specification) | 2026-09-27 | `SKILL.md` frontmatter rules checked by CI |

## OpenAI (ChatGPT and Codex)

| Topic | Source | Retrieved | What this repository uses |
| --- | --- | --- | --- |
| Package your plugin | [developers.openai.com/plugins/build/plugins](https://developers.openai.com/plugins/build/plugins) | 2026-10-10 | Portable root manifest with `extensions.com.openai.interface`; root `mcp.json` |
| Authentication | [developers.openai.com/plugins/build/auth](https://developers.openai.com/plugins/build/auth) | 2026-10-10 | OAuth 2.1 with PKCE `S256`, protected-resource metadata, CIMD client registration, default OpenID scope requests |
| Connect and test | [developers.openai.com/plugins/deploy/connect-chatgpt](https://developers.openai.com/plugins/deploy/connect-chatgpt) | 2026-10-10 | **Add custom MCP server** and **Create as a plugin** steps at `chatgpt.com/plugins` |
| Build skills | [developers.openai.com/plugins/build/skills](https://developers.openai.com/plugins/build/skills) | 2026-09-27 | Provider-neutral skill instructions |
| Developer mode availability | [OpenAI Help Center: Developer mode and MCP apps in ChatGPT](https://help.openai.com/en/articles/12584461-developer-mode-and-mcp-apps-in-chatgpt) | 2026-10-10 | Plan prerequisites, admin settings and the read/fetch limitation for Pro |

## Anthropic (Claude)

| Topic | Source | Retrieved | What this repository uses |
| --- | --- | --- | --- |
| Claude custom connectors | [Get started with custom connectors using remote MCP](https://support.claude.com/en/articles/11175166-get-started-with-custom-connectors-using-remote-mcp) | 2026-10-10 | Custom connector steps, the **OAuth client** choice and plan prerequisites |
| Claude Code plugin manifest | [Plugin manifest reference](https://code.claude.com/docs/en/plugins/manifest-reference) | 2026-09-27 | `.claude-plugin/plugin.json` |
| Claude Code marketplace | [Create a marketplace](https://code.claude.com/docs/en/plugins/create-marketplace) and [Marketplace reference](https://code.claude.com/docs/en/plugins/marketplace-reference) | 2026-10-10 (create), 2026-09-27 (reference) | `.claude-plugin/marketplace.json` with the repository root as the plugin source |
| Claude Code MCP servers | [Connect Claude Code to tools via MCP](https://code.claude.com/docs/en/mcp) | 2026-10-10 | `.mcp.json` with `"type": "http"`; OAuth discovery and CIMD support |
| Plugin validation | [Plugin commands reference](https://code.claude.com/docs/en/plugins/cli-reference) | 2026-09-27 | `claude plugin validate --strict` in CI |

## xAI (Grok)

| Topic | Source | Retrieved | What this repository uses |
| --- | --- | --- | --- |
| Grok connectors | [docs.x.ai/grok/connectors](https://docs.x.ai/grok/connectors) | 2026-10-10 (page updated 2026-10-06) | Custom MCP connector steps on grok.com |
| Business and Enterprise | [docs.x.ai/grok/connector-management](https://docs.x.ai/grok/connector-management) | 2026-10-10 (page updated 2026-10-06) | Admin provisioning in the xAI console |
| Grok Build plugins | [Skills, Plugins & Marketplaces](https://docs.x.ai/build/features/skills-plugins-marketplaces) | 2026-10-10 (page updated 2026-08-11) | Grok Build reads Claude Code plugins and marketplaces |

## Perplexity

| Topic | Source | Retrieved | What this repository uses |
| --- | --- | --- | --- |
| Launch of custom connectors | [What we shipped, March 13, 2026](https://www.perplexity.ai/changelog/what-we-shipped---march-13-2026) | 2026-10-10 | Pro, Max and Enterprise availability |
| Custom remote connectors | [Adding Custom Remote Connectors](https://www.perplexity.ai/help-center/en/articles/13915507-adding-custom-remote-connectors) | 2026-10-10 (page modified 2026-09-03) | Connector form fields, OAuth client ID when dynamic registration is unavailable, organization-wide sign-in |

## Protocol

| Topic | Source | Retrieved |
| --- | --- | --- |
| MCP authorization | [modelcontextprotocol.io authorization specification](https://modelcontextprotocol.io/specification/2025-11-25/basic/authorization) | 2026-09-27 |
