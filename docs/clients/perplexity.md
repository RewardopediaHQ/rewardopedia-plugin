# Connect Rewardopedia to Perplexity

**Status: unverified.** No Rewardopedia connection has been tested in
Perplexity, and the Rewardopedia MCP server (`https://mcp.rewardopedia.com/mcp`)
is not live yet. These steps come from Perplexity's documentation (retrieved
2026-09-27) and will be confirmed or corrected when the service launches. See
the [compatibility table](../compatibility.md).

## Before you connect

Read [Privacy, memory, retention and deletion](../privacy-and-memory.md). It
explains what Rewardopedia saves to your account, what you should never share,
and how to inspect or delete saved context.

## Surface and account prerequisites

- **Surface:** a custom remote connector in Perplexity (perplexity.ai).
- **Account:** Perplexity announced custom connectors for Pro, Max and
  Enterprise subscribers. In Enterprise organizations, members can add their
  own connectors only if an admin allows it.
- **Rewardopedia:** a Rewardopedia account to sign in with during OAuth.
- **OAuth client registration:** pending. Perplexity asks for a client ID and
  secret when a server does not support dynamic client registration.
  Rewardopedia will publish the Perplexity setup values in this guide before
  release. Do not use client credentials from any other source.

## Connect

1. Open **Account settings > Connectors**.
2. Select **+ Custom connector**, then **Remote**.
3. Enter the name `Rewardopedia` and the MCP server URL
   `https://mcp.rewardopedia.com/mcp`.
4. Set **Authentication** to **OAuth** and **Transport** to
   **Streamable HTTP**.
5. Read and accept the custom connector acknowledgement, then select **Add**.
6. Select the Rewardopedia connector card to sign in to Rewardopedia and
   review the requested permissions: `cards:read`, `context:read` and
   `context:write`.

Enterprise admins can add the connector for the whole organization from
**Enterprise settings > Permissions > Connectors permissions**; each member
should still sign in with their own Rewardopedia account.

## Try it

- "Using Rewardopedia, compare two cards I name and keep the fees and
  conditions attached."
- "Using Rewardopedia, what do you remember about me?"
- "Using Rewardopedia, suggest cards for my dining goal. Tell me what you will
  save first."

## Disconnect and delete

- To delete saved context, ask: "Using Rewardopedia, forget everything you
  remember about me." Deleting context is separate from disconnecting.
- To revoke access, open the connector's menu in **Account settings >
  Connectors** and remove it.

## Developer surfaces

Perplexity's developer API also accepts remote MCP servers. Developer API calls
are not consumer Perplexity verification and are not covered by this guide.

## Sources

- [Adding Custom Remote Connectors](https://www.perplexity.ai/help-center/en/articles/13915507-adding-custom-remote-connectors)
- [What we shipped, March 13, 2026](https://www.perplexity.ai/changelog/what-we-shipped---march-13-2026)
