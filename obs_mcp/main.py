"""OBS-MCP server entry point."""

import logging
import sys

from mcp.server.fastmcp import FastMCP

from obs_mcp.obs_client import OBSClient
from obs_mcp.tool_registry import register_all_tools

logging.basicConfig(level=logging.INFO, stream=sys.stderr)
logger = logging.getLogger(__name__)

client = OBSClient()

mcp = FastMCP(
    "obs-mcp",
    instructions=(
        "Control OBS Studio via obs-websocket v5. Requires OBS Studio running "
        "with Tools > WebSocket Server Settings enabled. Connection defaults "
        "to localhost:4455 with no password — override with OBS_HOST/OBS_PORT/"
        "OBS_PASSWORD environment variables if yours differs.\n\n"
        "Scene and source names are case-sensitive and must match exactly "
        "what's shown in OBS. Use get_scene_list / get_input_list to see "
        "exact names before acting on them."
    ),
)

register_all_tools(mcp)


def main():
    mcp.run()


if __name__ == "__main__":
    main()
