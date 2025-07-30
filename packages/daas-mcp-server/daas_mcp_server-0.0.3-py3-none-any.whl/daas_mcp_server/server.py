"""DaaS MCP Server."""

from daas_mcp_server.tools import (
    check_ddc_power_state,
    get_delivery_groups,
    get_machine_catalogs,
    getHypervisors,
    getHypervisor,
    getSessionsTrend
)
from daas_mcp_server.utils.logging import configure_logging, get_logger
from mcp.server.fastmcp import FastMCP

logger = get_logger(__name__)
configure_logging()

# Create an MCP server
mcp = FastMCP("daas_mcp_server", log_level="ERROR")

# Register tools
mcp.tool()(check_ddc_power_state)
mcp.tool()(get_delivery_groups)
mcp.tool()(get_machine_catalogs)
mcp.tool()(getHypervisors)
mcp.tool()(getHypervisor)
mcp.tool()(getSessionsTrend)


def main():
    """Run the MCP server."""
    logger.info("Starting the DaaS MCP Server")
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
