import os
import traceback
from ..server_instance import mcp
from ..utils.wallet import generate_new_wallet, get_address_from_private_key, WalletError

@mcp.tool()
def top_up(random_string: str = "default") -> str:
    """
    Provides a deposit address for the user's wallet.
    If the EOLAS_PRIVATE_KEY environment variable is not set, it generates a new wallet
    and provides instructions for configuration.
    """
    private_key = os.getenv("EOLAS_PRIVATE_KEY")

    if private_key:
        # If the private key is set, derive the address and return it.
        try:
            address = get_address_from_private_key(private_key)
            return (
                f"**Your Deposit Address (Base Network):**\n`{address}`\n\n"
                f"Send ETH to this address on the Base network to top up your account."
            )
        except WalletError as e:
            return f"Error: Could not derive address from the provided EOLAS_PRIVATE_KEY. Please check if it's correct. Details: {e}"
        except Exception as e:
            tb_str = traceback.format_exc()
            return f"An unexpected error occurred while deriving the address: {e}\n\nTraceback:\n{tb_str}"
    else:
        # If the private key is NOT set, generate a new wallet and provide instructions.
        try:
            new_wallet = generate_new_wallet()
            address = new_wallet['address']
            new_private_key = new_wallet['privateKey']
            
            return (
                f"**⚠️ ACTION REQUIRED: Configure Your Wallet ⚠️**\n\n"
                f"A new wallet has been generated for you as the `EOLAS_PRIVATE_KEY` environment variable was not found.\n\n"
                f"**1. Copy Your New Private Key:**\n"
                f"`{new_private_key}`\n\n"
                f"**🔐 THIS IS A SECRET!** Store it securely and do not share it. You will only see it this one time.\n\n"
                f"**2. Set the Environment Variable:**\n"
                f"Replace the existing `eolas-mech-mcp` entry in your MCP client's configuration file (e.g., `mcp.json` or `claude_desktop_config.json`) with the following block. This ensures the server uses your new wallet:\n"
                "```json\n"
                '"eolas-mech-mcp": {\n'
                '  "command": "npx",\n'
                '  "args": ["-y", "eolas-mech-mcp@latest"],\n'
                '  "env": {\n'
                '    "EOLAS_PRIVATE_KEY": "' + new_private_key + '"\n'
                '  }\n'
                '}\n'
                "```\n\n"
                f"**3. Your Deposit Address:**\n"
                f"Once configured, future runs of this tool will simply show your deposit address. You can send ETH on the Base network to:\n"
                f"`{address}`"
            )
        except Exception as e:
            tb_str = traceback.format_exc()
            return f"Error: Failed to generate a new wallet. Details: {e}\n\nTraceback:\n{tb_str}" 