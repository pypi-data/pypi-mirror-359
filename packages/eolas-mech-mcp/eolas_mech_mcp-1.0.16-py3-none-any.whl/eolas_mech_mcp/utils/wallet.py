"""
Stateless Wallet Utilities for Eolas MCP Server.
"""

import os
import logging
from eth_account import Account

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class WalletError(Exception):
    """Custom exception for wallet errors."""
    pass

def generate_new_wallet():
    """
    Generates a new Ethereum wallet.

    Returns:
        dict: A dictionary containing the public address and the private key.
    """
    try:
        acct = Account.create()
        private_key = acct.key.hex()
        address = acct.address
        logger.info(f"Generated new wallet with address: {address}")
        return {"address": address, "privateKey": private_key}
    except Exception as e:
        logger.error(f"Failed to generate new wallet: {e}", exc_info=True)
        raise WalletError(f"Could not generate a new wallet: {e}")

def get_address_from_private_key(private_key: str):
    """
    Derives the public Ethereum address from a private key.

    Args:
        private_key (str): The private key hex string.

    Returns:
        str: The public Ethereum address.
    """
    if not private_key:
        raise WalletError("Private key cannot be empty.")
    
    try:
        acct = Account.from_key(private_key)
        address = acct.address
        logger.info(f"Derived address {address} from private key.")
        return address
    except Exception as e:
        logger.error(f"Failed to derive address from private key: {e}", exc_info=True)
        raise WalletError(f"Invalid private key provided: {e}")

 