# Connect Rewardopedia to Grok

**Status: unverified.** No Rewardopedia connection has been tested in Grok, and
the Rewardopedia MCP server (`https://mcp.rewardopedia.com/mcp`) is not live
yet. These steps come from xAI's documentation (rechecked 2026-10-10) and will
be confirmed or corrected when the service launches. See the
[compatibility table](../compatibility.md).

## Before you connect

Read [Privacy, memory, retention and deletion](../privacy-and-memory.md). It
explains what Rewardopedia saves to your account, what you should never share,
and how to inspect or delete saved context.

## Surface and account prerequisites

- **Surface:** a custom MCP connector on [grok.com](https://grok.com/connectors).
- **Account:** xAI states connectors are available to all Grok users. On Grok
  Business and Enterprise plans, a team admin must first add the connector in
  the xAI console.
- **Rewardopedia:** a Rewardopedia account to sign in with during OAuth.
- **OAuth client registration:** pending. xAI does not document how Grok
  identifies itself to an OAuth server, and Rewardopedia turns off automatic
  client registration. Grok is admitted only after a live test; if the
  connector form asks for an OAuth client ID, Rewardopedia will publish the
  public client ID for Grok in this guide before release. There is no client
  secret. Do not use client credentials from any other source.

## Connect

1. Go to [grok.com/connectors](https://grok.com/connectors).
2. Select **New Connector**, then **Custom**.
3. Enter the MCP server URL `https://mcp.rewardopedia.com/mcp`.
4. Complete authentication by signing in to Rewardopedia, and review the
   requested permissions: `cards:read`, `context:read` and `context:write`.

## Connect (Grok Business and Enterprise)

1. A team admin signs in to the xAI console, selects the team, and opens the
   connectors page.
2. The admin selects **+ Add Connector**, then **Other**, and enters
   `https://mcp.rewardopedia.com/mcp`.
3. Members connect their own Rewardopedia accounts at
   [grok.com/connectors](https://grok.com/connectors).

## Try it

- "Using Rewardopedia, compare two cards I name and keep the fees and
  conditions attached."
- "Using Rewardopedia, what do you remember about me?"
- "Using Rewardopedia, suggest cards for my dining goal. Tell me what you will
  save first."

## Disconnect and delete

- To delete saved context, ask: "Using Rewardopedia, forget everything you
  remember about me." Deleting context is separate from disconnecting.
- To revoke access, remove the connector at
  [grok.com/connectors](https://grok.com/connectors).

## Developer surface: Grok Build

xAI documents that Grok Build reads Claude Code plugins and marketplaces, so
this repository's `.claude-plugin/` manifests and `.mcp.json` may load there.
Signing in to Rewardopedia from Grok Build is not supported for version 0.1.0,
because its OAuth client is not pre-registered. This has not been tested and
does not count as consumer Grok verification.

## Sources

- [Grok Connectors](https://docs.x.ai/grok/connectors)
- [Grok Business and Enterprise: Connector Management](https://docs.x.ai/grok/connector-management)
- [Grok Build: Skills, Plugins & Marketplaces](https://docs.x.ai/build/features/skills-plugins-marketplaces)
