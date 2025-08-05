from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("mikelopster-product")

# Constants
mock_api_base = "https://68902e38944bf437b594f827.mockapi.io/api/1/:endpoint"

@mcp.tool()
async def get_blogs() -> Any:
    """Get all blogs via GET mock_api_base and return JSON."""
    async with httpx.AsyncClient() as client:
        response = await client.get(mock_api_base)
        return response.json()

if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')