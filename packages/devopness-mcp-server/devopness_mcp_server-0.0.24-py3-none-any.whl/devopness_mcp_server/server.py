from typing import Any

from mcp.server.fastmcp import FastMCP

from devopness_mcp_server.lib.tools import register_tools


def get_mcp_server(**settings: Any) -> FastMCP:  # noqa: ANN401
    server = FastMCP(
        "Devopness",
        **settings,
    )

    register_tools(server)

    return server
