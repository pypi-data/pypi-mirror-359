from ..server_instance import mcp

@mcp.tool()
def add(a: int, b: int) -> str:
    """Adds two numbers and returns the result."""
    result = a + b
    return f"The result is {result}" 