# Connect Rewardopedia to Claude

**Status: unverified.** No Rewardopedia connection has been tested in Claude,
and the Rewardopedia MCP server (`https://mcp.rewardopedia.com/mcp`) is not
live yet. These steps come from Anthropic's documentation (retrieved
2026-09-27) and will be confirmed or corrected when the service launches. See
the [compatibility table](../compatibility.md).

## Before you connect

Read [Privacy, memory, retention and deletion](../privacy-and-memory.md). It
explains what Rewardopedia saves to your account, what you should never share,
and how to inspect or delete saved context.

## Surface and account prerequisites

- **Surface:** a custom connector in Claude (claude.ai, Claude Desktop and
  Cowork). Claude connects to the server from Anthropic's cloud, not from your
  device.
- **Account:** Anthropic states custom connectors are available on Free, Pro,
  Max, Team and Enterprise plans. Free plans are limited to one custom
  connector. On Team and Enterprise plans an Owner must add the connector for
  the organization before members can connect.
- **Rewardopedia:** a Rewardopedia account to sign in with during OAuth.

## Connect (Pro and Max plans)

1. Go to **Customize > Connectors**.
2. Select **+**, then **Add custom connector**.
3. Enter the remote MCP server URL `https://mcp.rewardopedia.com/mcp`.
4. Leave **Advanced settings** empty. Claude discovers Rewardopedia's OAuth
   settings, so no OAuth client ID or secret is needed.
5. Select **Add**, then connect and sign in to Rewardopedia. Review the
   requested permissions: `cards:read`, `context:read` and `context:write`.
6. In a conversation, open the **+** menu, choose **Connectors**, and turn on
   Rewardopedia.

## Connect (Team and Enterprise plans)

1. An Owner or Primary Owner opens **Organization settings > Connectors**,
   selects **Add**, hovers over **Custom**, selects **Web**, and enters
   `https://mcp.rewardopedia.com/mcp`.
2. Each member then opens **Customize > Connectors**, finds Rewardopedia and
   selects **Connect** to sign in with their own Rewardopedia account.

## Try it

- "Using Rewardopedia, compare two cards I name and keep the fees and
  conditions attached."
- "Using Rewardopedia, what do you remember about me?"
- "Using Rewardopedia, suggest cards for my dining goal. Tell me what you will
  save first."

Review tool approval requests. Only choose "Allow always" for tools you are
comfortable running unsupervised; `forget_my_context` deletes data.

## Disconnect and delete

- To delete saved context, ask: "Using Rewardopedia, forget everything you
  remember about me." Deleting context is separate from disconnecting.
- To revoke access, remove the connector in **Customize > Connectors**.

## Developer surface: Claude Code

This repository is also a Claude Code plugin marketplace. A local installation
from a checkout loads the `card-recommendations` skill and the `rewardopedia`
MCP server entry (Claude Code 2.1.283, 2026-09-27); live tool calls have not
been tested. Developer surfaces do not count as consumer Claude verification.

```bash
claude plugin marketplace add RewardopediaHQ/rewardopedia-plugin
claude plugin install rewardopedia@rewardopedia
```

Then run `/mcp` in a session to sign in to the `rewardopedia` server.

## Sources

- [Get started with custom connectors using remote MCP](https://support.claude.com/en/articles/11175166-get-started-with-custom-connectors-using-remote-mcp)
- [Claude Code: Create a marketplace](https://code.claude.com/docs/en/plugins/create-marketplace)
- [Claude Code: Connect Claude Code to tools via MCP](https://code.claude.com/docs/en/mcp)
