"""Export the Rewardopedia MCP server's advertised tool contract for the plugin package.

Run from the monorepo's apps/mcp-server directory (it imports the server package):

    uv run python <plugin>/schemas/vendor/rewardopedia-mcp/export_tools.py "$(git rev-parse HEAD)" \
        > <plugin>/schemas/vendor/rewardopedia-mcp/tools.json

Each tool keeps its name, title, description, annotations and full input schema. Output
schemas are reduced to their top-level property names: examples show abridged results.
"""

import asyncio
import json
import sys

from rewardopedia_mcp.card_tools import register_card_tools
from rewardopedia_mcp.config import Settings
from rewardopedia_mcp.context_tools import register_context_tools
from rewardopedia_mcp.recommendation_tools import register_recommendation_tools
from rewardopedia_mcp.server import create_protocol
from rewardopedia_mcp.tools import UpstreamSlot


async def main(commit: str) -> None:
    server, _ = create_protocol(Settings(REWARDS_API_URL="http://127.0.0.1:8000"))
    upstream = UpstreamSlot()
    register_card_tools(server, upstream)
    register_recommendation_tools(server, upstream)
    register_context_tools(server, upstream)
    tools = []
    for tool in await server.list_tools():
        dumped = tool.model_dump(by_alias=True, exclude_none=True, mode="json")
        output = dumped.get("outputSchema", {})
        tools.append(
            {
                "name": dumped["name"],
                "title": dumped.get("title"),
                "description": dumped["description"],
                "annotations": dumped.get("annotations", {}),
                "inputSchema": dumped["inputSchema"],
                "outputProperties": sorted(output.get("properties", {})),
                "outputRequired": sorted(output.get("required", [])),
            }
        )
    json.dump(
        {"source": "RewardopediaHQ/rewardopedia-mono-repo", "commit": commit, "tools": tools},
        sys.stdout,
        indent=2,
        sort_keys=True,
    )
    sys.stdout.write("\n")


asyncio.run(main(sys.argv[1]))
