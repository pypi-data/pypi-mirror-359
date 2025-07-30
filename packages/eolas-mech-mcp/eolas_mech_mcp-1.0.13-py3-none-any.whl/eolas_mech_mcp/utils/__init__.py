"""Utilities package for Eolas MCP Server."""

from ..server_instance import mcp
from .wallet import WalletManager, WalletManagerError

wallet_manager = WalletManager()

__all__ = ['WalletManager', 'WalletManagerError'] 