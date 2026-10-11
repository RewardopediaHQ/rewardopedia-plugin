# Vendored schemas

Upstream schemas copied unchanged so validation works offline and cannot drift
silently.

| Directory | Upstream | Upstream commit | Retrieved | License |
| --- | --- | --- | --- | --- |
| `agent-plugins-1.0.0/` | [agent-plugins.org/schemas/1.0.0](https://agent-plugins.org/schemas/1.0.0/plugin.schema.json), source [agentplugins/agent-plugins-spec](https://github.com/agentplugins/agent-plugins-spec/tree/main/schemas/1.0.0) | `d92e6f443b8edcea42c039727a82afdc565779e2` | 2026-09-27 | Apache-2.0 ([`LICENSE-Apache-2.0.txt`](agent-plugins-1.0.0/LICENSE-Apache-2.0.txt)) |
| `rewardopedia-mcp/` | Rewardopedia MCP server tool contract, exported from the private Rewardopedia monorepo (`apps/mcp-server`) | `c0ff0afeb28386e08441122b2fd18995bfc8edc7` | 2026-10-10 | MIT (this repository) |

SHA-256 of the vendored files:

```text
0a4aad95ce337878ad38802ebf0daa3fde76abe3f65400c86bcbb1ec0b3ab883  agent-plugins-1.0.0/plugin.schema.json
6539175bfcdf43085855183e86da40ea94b166547a72b47ae9a0a390516d3acb  agent-plugins-1.0.0/mcp.schema.json
23e2a06c7208825ac1a6aad3910f5a5d4330fe720ba500ed22046cb7a100d923  rewardopedia-mcp/tools.json
```

The validator checks these hashes. To update, download the new upstream files,
update this table and the hashes in the same pull request, and rerun
`uv run python scripts/validate.py all`.

## Rewardopedia tool contract

`rewardopedia-mcp/tools.json` holds each tool's name, title, description,
annotations and full input schema, plus the top-level field names of its
output. It is generated, not edited by hand, with
[`rewardopedia-mcp/export_tools.py`](rewardopedia-mcp/export_tools.py), run
from the monorepo's `apps/mcp-server` directory:

```bash
uv run python <plugin>/schemas/vendor/rewardopedia-mcp/export_tools.py "$(git rev-parse HEAD)" \
  > <plugin>/schemas/vendor/rewardopedia-mcp/tools.json
```

The schema check validates every example's tool-call arguments against these
input schemas, with no extra arguments allowed, and rejects result fields a
tool does not return. When the server's tools change, regenerate the file,
update the commit, date and hash above, and fix the examples and the
[tool reference](../../skills/card-recommendations/references/tools.md) in the
same pull request.
