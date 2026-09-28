# Packaging and client sources

Every packaging format and client setup step in this repository is based on the
official documentation below. All pages were retrieved on **2026-09-27**.
Client products change often: recheck each source before verifying a client or
cutting a release, and update the retrieval date when you do.

## Portable package (Agent Plugins and Agent Skills)

| Topic | Source | What this repository uses |
| --- | --- | --- |
| Agent Plugins 1.0.0 overview | [agent-plugins.org](https://agent-plugins.org/) | Root `plugin.json`, root `mcp.json`, `skills/` layout |
| Plugin manifest schema | [plugin.schema.json](https://agent-plugins.org/schemas/1.0.0/plugin.schema.json) | Vendored copy in `schemas/vendor/agent-plugins-1.0.0/` |
| MCP configuration schema | [mcp.schema.json](https://agent-plugins.org/schemas/1.0.0/mcp.schema.json) | Vendored copy; `streamable-http` transport |
| Agent Skills format | [agentskills.io/specification](https://agentskills.io/specification) | `SKILL.md` frontmatter rules checked by CI |

## OpenAI (ChatGPT and Codex)

| Topic | Source | What this repository uses |
| --- | --- | --- |
| Package your plugin | [developers.openai.com/plugins/build/plugins](https://developers.openai.com/plugins/build/plugins) | Portable root manifest with `extensions.com.openai.interface`; root `mcp.json` |
| Authentication | [developers.openai.com/plugins/build/auth](https://developers.openai.com/plugins/build/auth) | OAuth 2.1 with PKCE `S256`, protected-resource metadata, CIMD client registration |
| Connect and test | [developers.openai.com/plugins/deploy/connect-chatgpt](https://developers.openai.com/plugins/deploy/connect-chatgpt) | Developer mode and `chatgpt.com/plugins` connection steps |
| Build skills | [developers.openai.com/plugins/build/skills](https://developers.openai.com/plugins/build/skills) | Provider-neutral skill instructions |
| Developer mode availability | [OpenAI Help Center: Developer mode and MCP apps in ChatGPT](https://help.openai.com/en/articles/12584461-developer-mode-and-mcp-apps-in-chatgpt) | Plan prerequisites and the read/fetch limitation for individual plans |

## Anthropic (Claude)

| Topic | Source | What this repository uses |
| --- | --- | --- |
| Claude custom connectors | [Get started with custom connectors using remote MCP](https://support.claude.com/en/articles/11175166-get-started-with-custom-connectors-using-remote-mcp) | Custom connector steps and plan prerequisites |
| Claude Code plugin manifest | [Plugin manifest reference](https://code.claude.com/docs/en/plugins/manifest-reference) | `.claude-plugin/plugin.json` |
| Claude Code marketplace | [Create a marketplace](https://code.claude.com/docs/en/plugins/create-marketplace) and [Marketplace reference](https://code.claude.com/docs/en/plugins/marketplace-reference) | `.claude-plugin/marketplace.json` with the repository root as the plugin source |
| Claude Code MCP servers | [Connect Claude Code to tools via MCP](https://code.claude.com/docs/en/mcp) | `.mcp.json` with `"type": "http"`; OAuth discovery and CIMD support |
| Plugin validation | [Plugin commands reference](https://code.claude.com/docs/en/plugins/cli-reference) | `claude plugin validate --strict` in CI |

## xAI (Grok)

| Topic | Source | What this repository uses |
| --- | --- | --- |
| Grok connectors | [docs.x.ai/grok/connectors](https://docs.x.ai/grok/connectors) | Custom MCP connector steps on grok.com |
| Business and Enterprise | [docs.x.ai/grok/connector-management](https://docs.x.ai/grok/connector-management) | Admin provisioning in the xAI console |
| Grok Build plugins | [Skills, Plugins & Marketplaces](https://docs.x.ai/build/features/skills-plugins-marketplaces) | Grok Build reads Claude Code plugins and marketplaces |

## Perplexity

| Topic | Source | What this repository uses |
| --- | --- | --- |
| Launch of custom connectors | [What we shipped, March 13, 2026](https://www.perplexity.ai/changelog/what-we-shipped---march-13-2026) | Pro, Max and Enterprise availability |
| Custom remote connectors | [Adding Custom Remote Connectors](https://www.perplexity.ai/help-center/en/articles/13915507-adding-custom-remote-connectors) | Connector form fields, OAuth options and redirect URL |

## Protocol

| Topic | Source |
| --- | --- |
| MCP authorization | [modelcontextprotocol.io authorization specification](https://modelcontextprotocol.io/specification/2025-11-25/basic/authorization) |
