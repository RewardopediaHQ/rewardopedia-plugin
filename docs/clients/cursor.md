# Connect Rewardopedia to Cursor

**Status: unverified.** Package compatibility and OAuth/tool acceptance must be
verified on the installed Cursor version before this surface is advertised.

Read [privacy and memory](../privacy-and-memory.md) first. All card tool calls
record sanitized request history; a read-only client plan is not sufficient.

Cursor accepts portable Agent Plugins using the root `plugin.json`. Install
from this public repository using the current documented local/plugin workflow,
then inspect the `rewardopedia` remote MCP entry at
`https://mcp.rewardopedia.com/mcp`. Complete OAuth only after the operator has
verified the client's exact registration and redirect prerequisites. Never
paste an operator token or client secret into the package.

Try a source-backed card search, then ask for a Spanish US dining shortlist.
Inspect saved context, correct a stated goal and delete it. Record exact app,
package and deployed versions, both language pairs, isolation and failure cases
in the [compatibility table](../compatibility.md). A loaded manifest is not a
successful connection or functional qualification.

Marketplace submission requires a public repository and platform review. Local
installation, approval and an available public listing remain separate states.

Source: [Cursor Plugins reference](https://cursor.com/docs/reference/plugins)
(checked 2026-10-18).
