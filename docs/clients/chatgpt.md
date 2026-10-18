# Connect Rewardopedia to ChatGPT

**Status: unverified.** The service is deployed, but functional acceptance
on this surface is pending. Setup steps must be checked against the current
client UI and OAuth prerequisites. See the [compatibility table](../compatibility.md).

## Before you connect

Read [Privacy, memory, retention and deletion](../privacy-and-memory.md). It
explains what Rewardopedia saves to your account, what you should never share,
and how to inspect or delete saved context.

## Surface and account prerequisites

- **Surface:** ChatGPT on the web (`chatgpt.com`) using a developer-mode
  custom MCP server.
- **Account:** a ChatGPT account where developer mode is available. OpenAI's
  help center says full MCP support, including write actions, is for
  Business, Enterprise and Edu workspaces, where admins and owners control
  developer mode, and that Pro users can connect MCP servers with read/fetch
  permissions in developer mode. Every Rewardopedia card tool records sanitized request history. A
  read/fetch-only client cannot qualify for this flow; verify current plan
  support before connecting.
- **Rewardopedia:** a Rewardopedia account to sign in with during OAuth.
- **Sign-in information shared with ChatGPT:** ChatGPT requests the OpenID
  scopes (`openid`, `email`, `profile`), and Rewardopedia grants them to
  ChatGPT. Signing in shares your name, username, avatar and email address
  with ChatGPT. The sign-in consent screen lists them before you approve.
- A listing in the ChatGPT plugin directory is a separate, later step and is
  not available yet.

## Connect

1. Turn on developer mode in **Settings > Apps > Advanced settings**. On
   Business, Enterprise and Edu workspaces an admin or owner must allow it
   first (Business: **Workspace settings > Permissions & roles**; Enterprise
   and Edu can also grant it to selected members).
2. Go to [ChatGPT Plugins](https://chatgpt.com/plugins), select the plus
   button, then **Add custom MCP server**.
3. Enter the name `Rewardopedia` and a short description.
4. Under **Connection**, enter the MCP server URL
   `https://mcp.rewardopedia.com/mcp`.
5. Configure authentication as OAuth. ChatGPT discovers Rewardopedia's OAuth
   settings and identifies itself with its own client metadata document, so
   you do not need to enter a client ID or secret.
6. Review the risk warning, select **I understand and want to continue**, then
   **Create as a plugin**, and review the tools ChatGPT discovered.
7. When prompted, sign in to Rewardopedia and review the requested
   permissions: `openid`, `email` and `profile`, plus `cards:read`,
   `context:read` and `context:write`. Signing in shares your name, username,
   avatar and email address with ChatGPT. The consent screen lists them
   before you approve.
8. Start a new chat, type `@` in the prompt box and select Rewardopedia.

## Try it

- "Using Rewardopedia, compare two cards I name and keep the fees and
  conditions attached."
- "Using Rewardopedia, what do you remember about me?"
- "Using Rewardopedia, suggest cards for my dining goal. Tell me what you will
  save first."

## Disconnect and delete

- To delete saved context, ask: "Using Rewardopedia, forget everything you
  remember about me." Deleting context is separate from disconnecting.
- To revoke access, remove or disconnect the Rewardopedia plugin at
  [ChatGPT Plugins](https://chatgpt.com/plugins).

## Developer surface: Codex and the ChatGPT desktop app

This repository's root `plugin.json` and `mcp.json` follow OpenAI's portable
plugin layout. On 2026-09-27 a local Codex CLI installation from a checkout
listed the plugin and its MCP server entry. Codex and ChatGPT desktop each require approved OAuth prerequisites and
actual tool-call evidence. Current web-client registration is not proof of
access. They qualify independently; package loading alone does not qualify ChatGPT web.

## Sources

- [Connect and test your plugin](https://developers.openai.com/plugins/deploy/connect-chatgpt)
- [Authentication](https://developers.openai.com/plugins/build/auth)
- [Package your plugin](https://developers.openai.com/plugins/build/plugins)
- [OpenAI Help Center: Developer mode and MCP apps in ChatGPT](https://help.openai.com/en/articles/12584461-developer-mode-and-mcp-apps-in-chatgpt)
