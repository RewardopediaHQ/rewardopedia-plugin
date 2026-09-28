"""Facts the package must keep consistent across manifests and documentation."""

from __future__ import annotations

PLUGIN_NAME = "rewardopedia"
MCP_SERVER_NAME = "rewardopedia"
SERVICE_HOST = "mcp.rewardopedia.com"
CANONICAL_ENDPOINT = f"https://{SERVICE_HOST}/mcp"
# Rewardopedia's own domain; any other host naming Rewardopedia is a lookalike.
BRAND_DOMAIN = "rewardopedia.com"

# Set to True in the launch pull request that removes the README's NOT YET LIVE
# banner (see CONTRIBUTING.md). While False, the README must carry the banner
# and external link checks skip the not-yet-reachable service host.
SERVICE_LIVE = False

REPOSITORY_URL = "https://github.com/RewardopediaHQ/rewardopedia-plugin"
LICENSE_ID = "MIT"

# The eleven MCP tools, in documentation order.
TOOLS = (
    "search_cards",
    "get_card_detail",
    "compare_cards",
    "get_card_offers",
    "get_card_benefits",
    "get_earning_rates",
    "get_card_fees",
    "recommend_cards",
    "get_my_context",
    "update_my_context",
    "forget_my_context",
)

SCOPES = ("cards:read", "context:read", "context:write")

# Manifests that carry the plugin release version.
VERSIONED_MANIFESTS = ("plugin.json", ".claude-plugin/plugin.json")
MARKETPLACE = ".claude-plugin/marketplace.json"

# Hosts that are intentionally not reachable yet; external link checks skip them.
NOT_YET_LIVE_HOSTS: frozenset[str] = frozenset() if SERVICE_LIVE else frozenset({SERVICE_HOST})

# Consumer clients that must each have a guide and a compatibility row.
CONSUMER_CLIENTS = ("ChatGPT", "Claude", "Grok", "Perplexity")
CLIENT_GUIDES = {
    "ChatGPT": "docs/clients/chatgpt.md",
    "Claude": "docs/clients/claude.md",
    "Grok": "docs/clients/grok.md",
    "Perplexity": "docs/clients/perplexity.md",
}
