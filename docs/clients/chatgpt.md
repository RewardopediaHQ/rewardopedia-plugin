# Connect Rewardopedia to ChatGPT

**Status: unverified.** The service is deployed, but functional acceptance
on this surface is pending. Setup steps must be checked against the current
client UI and OAuth prerequisites. See the [compatibility table](../compatibility.md).

## Before you connect

Read [Privacy, memory, retention and deletion](../privacy-and-memory.md). It
explains what Rewardopedia saves to your account, what you should never share,
and how to inspect or delete saved context.

## Surface and account prerequisites

- **Surface:** ChatGPT on the web (`chatgpt.com`) using a custom MCP server
  from Plugins.
- **Account:** a workspace that permits custom MCP connections and write
  actions. OpenAI documents full MCP for Business and Enterprise/Edu; Business
  requires an admin or owner, while Enterprise/Edu can authorize members through
  RBAC. Pro has read/fetch access only. Every Rewardopedia card tool records
  sanitized request history, so a read/fetch-only connection cannot qualify the
  complete flow. Verify the actual workspace permissions before connecting.
- **Rewardopedia:** a Rewardopedia account to sign in with during OAuth.
- **Sign-in information shared with ChatGPT:** ChatGPT requests the OpenID
  scopes (`openid`, `email`, `profile`), and Rewardopedia grants them to
  ChatGPT. Signing in shares your name, username, avatar and email address
  with ChatGPT. The sign-in consent screen lists them before you approve.
- A listing in the ChatGPT plugin directory is a separate, later step and is
  not available yet.

## Connect

1. Check your workspace's **Create plugins with MCPs** permission. The current
   Plugins flow does not require turning on Developer Mode; each server has its
   own risk acknowledgment. Legacy Apps screens may differ.
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

This repository's root `plugin.json` and `mcp.json` carry the portable plugin.
A historical Codex package-loading check on 2026-09-27 did not establish OAuth
or useful tool calls. Codex CLI, Codex desktop and ChatGPT desktop remain
independently unverified.

For a direct Codex CLI MCP connection, first read the privacy guide above, then:

```bash
codex mcp add rewardopedia --url https://mcp.rewardopedia.com/mcp
codex mcp login rewardopedia
```

If adding the server already completes OAuth, the separate login is unnecessary.
These command options were checked in local CLI `0.163.0` on 2026-10-19; no
Rewardopedia login or client qualification was performed by that check.

Codex supports CIMD and can select it from the authorization server's advertised
capabilities. Rewardopedia advertises CIMD and issuer-bound responses, but
admission of the actual Codex client is still unverified. Review the displayed
Rewardopedia consent before approving it. Do not reuse ChatGPT web's client ID
or callback for Codex. If admission fails, retain only a sanitized error and ask
Rewardopedia support to verify that client's registration. Any pre-registered
fallback must use the exact callback shown by the installed CLI.

In a fresh Codex conversation, exercise the card and context examples above in
both US languages. Record the app version, deployed build, tool arguments and
sanitized results. A direct MCP connection tests the server; separately verify
installation of the portable package and its skill before claiming plugin
compatibility. Public stable-release and directory availability remain pending.

Both surfaces require source/date links, context reuse/correction/deletion,
two-account isolation, reconnect and failure evidence before their compatibility
row can change. Signing in on ChatGPT web does not qualify Codex or a desktop app.

## Sources

- [Connect and test your plugin](https://developers.openai.com/plugins/deploy/connect-chatgpt)
- [Authentication](https://developers.openai.com/plugins/build/auth)
- [Package your plugin](https://developers.openai.com/plugins/build/plugins)
- [OpenAI Help Center: Connecting custom MCP servers](https://help.openai.com/en/articles/12584461-connecting-custom-mcp-servers-in-chatgpt)
- [Codex MCP configuration and OAuth](https://learn.chatgpt.com/docs/extend/mcp?surface=cli)
