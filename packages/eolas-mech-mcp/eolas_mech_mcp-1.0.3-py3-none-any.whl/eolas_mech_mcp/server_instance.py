from mcp.server.fastmcp import FastMCP

# This shared instance will be used by tools to register themselves.
mcp = FastMCP(
    "eolas-mcp-server",
    version="0.1.0-python"
) 