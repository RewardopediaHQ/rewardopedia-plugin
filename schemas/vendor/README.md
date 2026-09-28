# Vendored schemas

Upstream schemas copied unchanged so validation works offline and cannot drift
silently.

| Directory | Upstream | Upstream commit | Retrieved | License |
| --- | --- | --- | --- | --- |
| `agent-plugins-1.0.0/` | [agent-plugins.org/schemas/1.0.0](https://agent-plugins.org/schemas/1.0.0/plugin.schema.json), source [agentplugins/agent-plugins-spec](https://github.com/agentplugins/agent-plugins-spec/tree/main/schemas/1.0.0) | `d92e6f443b8edcea42c039727a82afdc565779e2` | 2026-09-27 | Apache-2.0 ([`LICENSE-Apache-2.0.txt`](agent-plugins-1.0.0/LICENSE-Apache-2.0.txt)) |

SHA-256 of the vendored files:

```text
0a4aad95ce337878ad38802ebf0daa3fde76abe3f65400c86bcbb1ec0b3ab883  agent-plugins-1.0.0/plugin.schema.json
6539175bfcdf43085855183e86da40ea94b166547a72b47ae9a0a390516d3acb  agent-plugins-1.0.0/mcp.schema.json
```

The validator checks these hashes. To update, download the new upstream files,
update this table and the hashes in the same pull request, and rerun
`uv run python scripts/validate.py all`.
