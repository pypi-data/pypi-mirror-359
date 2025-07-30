from ..server_instance import mcp
from ..utils.wallet import wallet_manager

@mcp.tool()
def top_up() -> str:
    """Top up the balance of the user. Provides a deposit address or generates a wallet if needed."""
    if wallet_manager.has_wallet():
        address = wallet_manager.get_wallet_address()
        return f"**Deposit Address:** {address}\n\nSend ETH to the address above to add funds."
    else:
        wallet_info = wallet_manager.generate_wallet()
        address = wallet_info['address']
        private_key = wallet_info['privateKey']
        return (
            f"**⚠️ IMPORTANT: NEW WALLET GENERATED ⚠️**\n\n"
            f"**Deposit Address:** {address}\n\n"
            f"**Private Key:** {private_key}\n\n"
            f"**🔐 SECURITY WARNING:**\n"
            f"• Store this private key securely - you will only see it once!\n"
            f"• Use this wallet exclusively for MCP top-ups\n"
            f"• Never share this private key with anyone\n"
            f"• Consider backing it up in a secure location\n\n"
            f"Send ETH to the address above to add funds."
        ) 