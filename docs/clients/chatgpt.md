# Connect Rewardopedia to ChatGPT

**Status: unverified.** No Rewardopedia connection has been tested in ChatGPT,
and the Rewardopedia MCP server (`https://mcp.rewardopedia.com/mcp`) is not
live yet. These steps come from OpenAI's documentation (retrieved 2026-09-27)
and will be confirmed or corrected when the service launches. See the
[compatibility table](../compatibility.md).

## Before you connect

Read [Privacy, memory, retention and deletion](../privacy-and-memory.md). It
explains what Rewardopedia saves to your account, what you should never share,
and how to inspect or delete saved context.

## Surface and account prerequisites

- **Surface:** ChatGPT on the web (`chatgpt.com`) using a developer-mode
  connection to a remote MCP server.
- **Account:** a ChatGPT account where developer mode is available. OpenAI
  states that availability depends on account and workspace policy. Its help
  center says full MCP support, including write actions, is for Business,
  Enterprise and Edu workspaces (where admins control developer mode), and that
  Pro users can connect MCP servers with read/fetch permissions. If your plan
  only allows read/fetch, saving, correcting and deleting context may be
  unavailable in ChatGPT; this has not been tested.
- **Rewardopedia:** a Rewardopedia account to sign in with during OAuth.
- A listing in the ChatGPT plugin directory is a separate, later step and is
  not available yet.

## Connect

1. In ChatGPT, open **Settings**, select **Security and login**, and turn on
   **Developer mode**. On Business, Enterprise and Edu workspaces an admin may
   need to enable or grant developer mode first.
2. Go to [ChatGPT Plugins](https://chatgpt.com/plugins) and select the plus
   button.
3. Enter the name `Rewardopedia` and a short description.
4. Under **Connection**, enter the MCP server URL
   `https://mcp.rewardopedia.com/mcp`.
5. Create the connection. ChatGPT discovers Rewardopedia's OAuth settings and
   identifies itself with its client metadata document, so you do not need to
   enter a client ID or secret.
6. When prompted, sign in to Rewardopedia and review the requested
   permissions: `cards:read`, `context:read` and `context:write`.
7. Start a new chat and add the Rewardopedia connection from the tools menu.

## Try it

- "Using Rewardopedia, compare two cards I name and keep the fees and
  conditions attached."
- "Using Rewardopedia, what do you remember about me?"
- "Using Rewardopedia, suggest cards for my dining goal. Tell me what you will
  save first."

## Disconnect and delete

- To delete saved context, ask: "Using Rewardopedia, forget everything you
  remember about me." Deleting context is separate from disconnecting.
- To revoke access, remove or disconnect the Rewardopedia connection at
  [ChatGPT Plugins](https://chatgpt.com/plugins).

## Developer surface: Codex and the ChatGPT desktop app

This repository's root `plugin.json` and `mcp.json` follow OpenAI's portable
plugin layout, and Codex reads the repository's marketplace file. A local
Codex CLI installation from a checkout lists the plugin and its MCP server
entry; installation in the ChatGPT desktop app and live tool calls have not
been tested. Developer surfaces do not count as consumer ChatGPT verification.

```bash
codex plugin marketplace add RewardopediaHQ/rewardopedia-plugin
codex plugin add rewardopedia@rewardopedia
```

## Sources

- [Connect and test your plugin](https://developers.openai.com/plugins/deploy/connect-chatgpt)
- [Authentication](https://developers.openai.com/plugins/build/auth)
- [Package your plugin](https://developers.openai.com/plugins/build/plugins)
- [OpenAI Help Center: Developer mode and MCP apps in ChatGPT](https://help.openai.com/en/articles/12584461-developer-mode-and-mcp-apps-in-chatgpt)
