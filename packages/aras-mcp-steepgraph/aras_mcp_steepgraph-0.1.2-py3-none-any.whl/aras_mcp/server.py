from mcp.server.fastmcp import FastMCP  # Commented out, update if needed
from .tools import test_api_connection, get_items, api_create_item
import mcp.types as types
# Create an MCP server
mcp = FastMCP("aras-mcp", port=5001)

mcp.add_tool(name="test api connection", description="this tool is used for checking mcp server is running and login into aras server and get token", fn=test_api_connection)

mcp.add_tool(
    name="get items",
    description="this tool is used for getting items from aras server using OData API",
    fn=get_items,
)

mcp.add_tool(
    name="create item",
    description="this tool is used for creating item in aras server using OData API",
    fn=api_create_item,
)
