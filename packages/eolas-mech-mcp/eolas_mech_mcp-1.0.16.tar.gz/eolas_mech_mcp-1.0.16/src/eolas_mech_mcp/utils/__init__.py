"""Eolas MCP Server Utilities"""

from .wallet import generate_new_wallet, get_address_from_private_key, WalletError

__all__ = [
    "generate_new_wallet",
    "get_address_from_private_key",
    "WalletError",
] 