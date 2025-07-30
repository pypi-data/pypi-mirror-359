from mcp.server.fastmcp import FastMCP

# This shared instance will be used by tools to register themselves.
mcp = FastMCP(
    "eolas-mech-mcp",
    version="1.0.14"
) 