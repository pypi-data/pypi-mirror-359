#!/usr/bin/env python3
"""
Eolas MCP Server - A Model Context Protocol server for wallet and computation tools.
Follows MCP best practices with proper error handling, configuration, and lifecycle management.
"""

import os
import logging
from pathlib import Path

from dotenv import load_dotenv

# Load environment variables from the project root
load_dotenv(dotenv_path=Path(__file__).parent.parent / '.env')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import the shared mcp instance
from .server_instance import mcp

# Import all tools to register them
from .tools import add, top_up

# --- Main Execution ---
def main():
    """Entry point for the MCP server."""
    logger.info("Preparing to start Eolas MCP Server...")
    try:
        mcp.run()
    except Exception as e:
        logger.error(f"Server failed to run: {e}", exc_info=True)
        raise 