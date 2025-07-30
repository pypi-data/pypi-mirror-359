from pydantic import BaseModel, ValidationError
from ..server_instance import mcp

class AddRequest(BaseModel):
    a: int
    b: int

@mcp.tool()
def add(a: int, b: int) -> str:
    """Adds two numbers and returns the result."""
    try:
        request = AddRequest(a=a, b=b)
        result = request.a + request.b
        return f"The result is {result}"
    except ValidationError as e:
        return f"Error: Invalid input - {str(e)}"
    except Exception as e:
        return f"Error: An unexpected error occurred: {e}" 