#!/usr/bin/env python3
"""
Eolas MCP Server - A Model Context Protocol server for wallet and computation tools.
Follows MCP best practices with proper error handling, configuration, and lifecycle management.
"""

import os
import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator
from pathlib import Path

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP, Context
from pydantic import BaseModel, ValidationError

# Load environment variables from the project root
load_dotenv(dotenv_path=Path(__file__).parent.parent / '.env')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# --- Pydantic Models for Input Validation ---
class AddRequest(BaseModel):
    a: int
    b: int

# --- Application Context ---
class AppContext(BaseModel):
    """Application context for shared resources like the wallet manager."""
    wallet_manager: object

# --- Server Lifecycle (Lifespan Manager) ---
@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[AppContext]:
    """Manage application lifecycle with proper startup and cleanup."""
    logger.info("Server startup: Initializing resources...")
    
    # Import here to ensure it's loaded within the module context
    from .utils.wallet import WalletManager, WalletManagerError
    
    try:
        # Configuration from environment
        ETH_RPC_URL = 'https://eth.llamarpc.com' # Hardcoded default
        WALLET_FILE_PATH = os.getenv('WALLET_FILE_PATH', './wallet.json')
        PASSWORD_FILE_PATH = os.getenv('PASSWORD_FILE_PATH', './password.txt')

        # Initialize wallet manager
        wallet_manager = WalletManager(
            wallet_file=WALLET_FILE_PATH,
            password_file=PASSWORD_FILE_PATH,
            eth_rpc_url=ETH_RPC_URL
        )
        logger.info("Wallet manager initialized successfully.")
        
        # Yield the context to the application
        yield AppContext(wallet_manager=wallet_manager)
        
    except WalletManagerError as e:
        logger.error(f"Fatal error during wallet manager initialization: {e}")
        # Not yielding will prevent the server from starting
    except Exception as e:
        logger.error(f"An unexpected fatal error occurred during startup: {e}")
        # Not yielding will prevent the server from starting
    finally:
        # This code runs on server shutdown
        logger.info("Server shutdown: Cleaning up resources...")

# --- MCP Server Instance ---
mcp = FastMCP(
    "eolas-mcp-server-python",
    version="1.0.0-best-practice",
    lifespan=app_lifespan
)

# --- MCP Tools ---
@mcp.tool()
def add(a: int, b: int, ctx: Context) -> str:
    """Adds two numbers and returns the result."""
    try:
        request = AddRequest(a=a, b=b)
        result = request.a + request.b
        ctx.info(f"Addition performed: {request.a} + {request.b} = {result}")
        return f"The result is {result}"
    except ValidationError as e:
        ctx.error(f"Invalid input for add tool: {e}")
        return f"Error: Invalid input - {str(e)}"
    except Exception as e:
        ctx.error(f"Unexpected error in add tool: {e}")
        return f"Error: An unexpected error occurred."

@mcp.tool()
def top_up(ctx: Context) -> str:
    """Tops up the user's balance. Provides a deposit address or generates a wallet if needed."""
    try:
        wallet_manager: WalletManager = ctx.request_context.lifespan_context.wallet_manager
        
        if wallet_manager.has_wallet():
            address = wallet_manager.get_wallet_address()
            ctx.info(f"Providing existing wallet address: {address}")
            return f"**Deposit Address:** {address}\n\nSend ETH to the address above to add funds."
        else:
            ctx.info("No existing wallet found. Generating a new one...")
            wallet_info = wallet_manager.generate_wallet()
            address = wallet_info['address']
            private_key = wallet_info['privateKey']
            ctx.info(f"New wallet generated: {address}")
            return (
                f"**⚠️ IMPORTANT: NEW WALLET GENERATED ⚠️**\n\n"
                f"**Deposit Address:** {address}\n\n"
                f"**Private Key:** {private_key}\n\n"
                f"**🔐 SECURITY WARNING:**\n"
                f"• Store this private key securely - you will only see it once!\n"
                f"• Use this wallet exclusively for MCP top-ups.\n"
                f"• Never share this private key with anyone.\n"
                f"• Consider backing it up in a secure location.\n\n"
                f"Send ETH to the address above to add funds."
            )
    except Exception as e:
        ctx.error(f"Error in top_up tool: {e}", exc_info=True)
        return "Error: Could not process the top-up request."

# --- MCP Resources ---
@mcp.resource("wallet://address")
def get_wallet_address() -> str:
    """Gets the current wallet address as a resource."""
    try:
        # The context is available on the mcp object during a request
        wallet_manager: WalletManager = mcp.request_context.lifespan_context.wallet_manager
        address = wallet_manager.get_wallet_address()
        return address if address else "No wallet found."
    except Exception as e:
        mcp.get_logger().error(f"Error retrieving wallet address: {e}", exc_info=True)
        return "Error: Could not retrieve wallet address."

@mcp.resource("wallet://balance")
def get_wallet_balance() -> str:
    """Gets the current wallet balance as a resource."""
    try:
        wallet_manager: WalletManager = mcp.request_context.lifespan_context.wallet_manager
        balance = wallet_manager.get_balance()
        return f"{balance} ETH"
    except Exception as e:
        mcp.get_logger().error(f"Error retrieving wallet balance: {e}", exc_info=True)
        return "Error: Could not retrieve wallet balance."

# --- Main Execution ---
def main():
    """Defines the main entry point for the MCP server, to be called by __main__.py."""
    try:
        logger.info("Preparing to start Eolas MCP Server...")
        mcp.run()
    except Exception as e:
        logger.error(f"Server failed to run: {e}", exc_info=True)
        raise 