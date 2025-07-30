"""hey MCP server tools."""
from mcp.server.fastmcp import FastMCP

# Create an MCP server
mcp = FastMCP("hey MCP")

@mcp.tool()
def add_two_numbers(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b

@mcp.tool()
def subtract_two_numbers(a: int, b: int) -> int:
    """Subtract two numbers."""
    return a - b
