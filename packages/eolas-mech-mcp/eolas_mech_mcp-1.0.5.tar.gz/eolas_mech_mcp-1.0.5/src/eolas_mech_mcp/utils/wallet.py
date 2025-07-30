"""
Secure Wallet Manager for Eolas MCP Server.
Follows security best practices with proper error handling and configuration.
"""

import json
import os
import secrets
import logging
from pathlib import Path
from typing import Optional, Dict, Any

import keyring
from Crypto.Cipher import AES
from web3 import Web3
from eth_account import Account

logger = logging.getLogger(__name__)

class WalletManagerError(Exception):
    """Custom exception for wallet manager errors"""
    pass

class WalletManager:
    """
    Secure wallet manager with encrypted storage and proper error handling.
    
    Features:
    - Encrypted private key storage using AES-GCM
    - Secure password management using system keyring
    - Configurable file paths and RPC endpoints
    - Comprehensive error handling and logging
    """
    
    SERVICE_NAME = "eolas-mcp-server"
    PASSWORD_KEY = "wallet-password"
    
    def __init__(self, wallet_file: str = "./wallet.json", 
                 password_file: str = "./password.txt",
                 eth_rpc_url: str = "https://eth.llamarpc.com"):
        """
        Initialize the wallet manager.
        
        Args:
            wallet_file: Path to the wallet file
            password_file: Path to the password file (fallback if keyring fails)
            eth_rpc_url: Ethereum RPC endpoint URL
        """
        self.wallet_file = Path(wallet_file)
        self.password_file = Path(password_file)
        self.eth_rpc_url = eth_rpc_url
        
        try:
            self.web3 = Web3(Web3.HTTPProvider(eth_rpc_url))
            if not self.web3.is_connected():
                logger.warning(f"Failed to connect to Ethereum RPC at {eth_rpc_url}")
        except Exception as e:
            logger.error(f"Failed to initialize Web3 connection: {e}")
            self.web3 = None
        
        self.wallet_data: Optional[Dict[str, Any]] = None
        self.password: Optional[str] = None
        
        self._load_password()
        self._load_wallet()

    def _load_password(self) -> None:
        """Load password from keyring or fallback to file."""
        try:
            # Try to load from system keyring first (more secure)
            self.password = keyring.get_password(self.SERVICE_NAME, self.PASSWORD_KEY)
            
            if self.password:
                logger.info("Password loaded from system keyring")
                return
            
            # Fallback to file-based storage
            if self.password_file.exists():
                with open(self.password_file, "r", encoding="utf-8") as f:
                    self.password = f.read().strip()
                logger.info("Password loaded from file (consider migrating to keyring)")
                
                # Try to migrate to keyring
                self._save_password_to_keyring(self.password)
                
        except Exception as e:
            logger.error(f"Failed to load password: {e}")

    def _save_password_to_keyring(self, password: str) -> bool:
        """
        Save password to system keyring.
        
        Args:
            password: Password to save
            
        Returns:
            True if successful, False otherwise
        """
        try:
            keyring.set_password(self.SERVICE_NAME, self.PASSWORD_KEY, password)
            logger.info("Password saved to system keyring")
            return True
        except Exception as e:
            logger.warning(f"Failed to save password to keyring: {e}")
            return False
    
    def _save_password_to_file(self, password: str) -> None:
        """
        Save password to file as fallback.
        
        Args:
            password: Password to save
        """
        try:
            with open(self.password_file, "w", encoding="utf-8") as f:
                f.write(password)
            # Set restrictive permissions
            os.chmod(self.password_file, 0o600)
            self.password = password
            logger.info("Password saved to file with restricted permissions")
        except Exception as e:
            logger.error(f"Failed to save password to file: {e}")
            raise WalletManagerError(f"Failed to save password: {e}")

    def set_password(self, password: Optional[str] = None) -> None:
        """
        Set a new password for wallet encryption.
        
        Args:
            password: Password to use, or None to generate a random one
        """
        if not password:
            password = secrets.token_hex(32)  # 64 character password
        
        # Try keyring first, fall back to file
        if not self._save_password_to_keyring(password):
            self._save_password_to_file(password)
        else:
            self.password = password

    def has_password(self) -> bool:
        """Check if a password is set."""
        return self.password is not None

    def _get_derived_key(self) -> bytes:
        """
        Get the derived encryption key from password.
        
        Returns:
            32-byte encryption key
            
        Raises:
            WalletManagerError: If no password is set
        """
        if not self.password:
            raise WalletManagerError("Password not set. Call set_password() first.")
        return self.password.ljust(32, '0')[:32].encode('utf-8')

    def _encrypt(self, text: str) -> Dict[str, str]:
        """
        Encrypt text using AES-GCM.
        
        Args:
            text: Text to encrypt
            
        Returns:
            Dictionary containing encrypted data and IV
        """
        try:
            key = self._get_derived_key()
            cipher = AES.new(key, AES.MODE_GCM)
            ciphertext, tag = cipher.encrypt_and_digest(text.encode('utf-8'))
            return {
                'encrypted': ciphertext.hex() + tag.hex(),
                'iv': cipher.nonce.hex()
            }
        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            raise WalletManagerError(f"Failed to encrypt data: {e}")

    def _decrypt(self, encrypted: str, iv_hex: str) -> str:
        """
        Decrypt text using AES-GCM.
        
        Args:
            encrypted: Encrypted data (hex string)
            iv_hex: Initialization vector (hex string)
            
        Returns:
            Decrypted text
        """
        try:
            key = self._get_derived_key()
            iv = bytes.fromhex(iv_hex)
            
            # The auth tag is the last 16 bytes (32 hex characters)
            auth_tag_hex = encrypted[-32:]
            encrypted_data_hex = encrypted[:-32]
            
            tag = bytes.fromhex(auth_tag_hex)
            ciphertext = bytes.fromhex(encrypted_data_hex)
            
            cipher = AES.new(key, AES.MODE_GCM, nonce=iv)
            decrypted_bytes = cipher.decrypt_and_verify(ciphertext, tag)
            return decrypted_bytes.decode('utf-8')
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            raise WalletManagerError(f"Failed to decrypt data: {e}")

    def _load_wallet(self) -> None:
        """Load wallet data from file."""
        if self.wallet_file.exists():
            try:
                with open(self.wallet_file, "r", encoding="utf-8") as f:
                    self.wallet_data = json.load(f)
                logger.info("Wallet data loaded successfully")
            except (IOError, json.JSONDecodeError) as e:
                logger.error(f"Failed to load wallet: {e}")

    def _save_wallet(self, wallet_data: Dict[str, Any]) -> None:
        """
        Save wallet data to file.
        
        Args:
            wallet_data: Wallet data to save
        """
        try:
            with open(self.wallet_file, "w", encoding="utf-8") as f:
                json.dump(wallet_data, f, indent=2)
            # Set restrictive permissions
            os.chmod(self.wallet_file, 0o600)
            self.wallet_data = wallet_data
            logger.info("Wallet data saved successfully")
        except Exception as e:
            logger.error(f"Failed to save wallet: {e}")
            raise WalletManagerError(f"Failed to save wallet: {e}")

    def generate_wallet(self) -> Dict[str, str]:
        """
        Generate a new Ethereum wallet.
        
        Returns:
            Dictionary containing address and private key
            
        Raises:
            WalletManagerError: If wallet generation fails
        """
        try:
            if not self.has_password():
                self.set_password()

            # Generate new account
            acct = Account.create()
            private_key = acct.key.hex()
            
            # Encrypt the private key
            encryption_result = self._encrypt(private_key)
            
            wallet_data = {
                'address': acct.address,
                'encryptedPrivateKey': encryption_result['encrypted'],
                'iv': encryption_result['iv'],
                'created_at': str(Path(__file__).stat().st_mtime)  # timestamp
            }
            
            self._save_wallet(wallet_data)
            logger.info(f"New wallet generated: {acct.address}")
            
            return {
                'address': acct.address,
                'privateKey': private_key
            }

        except Exception as e:
            logger.error(f"Failed to generate wallet: {e}")
            raise WalletManagerError(f"Failed to generate wallet: {e}")
    
    def get_wallet_address(self) -> Optional[str]:
        """
        Get the wallet address.
        
        Returns:
            Wallet address or None if no wallet exists
        """
        return self.wallet_data.get('address') if self.wallet_data else None

    def get_private_key(self) -> Optional[str]:
        """
        Get the decrypted private key.
        
        Returns:
            Private key or None if not available
        """
        if not self.wallet_data or not self.password:
            return None
        
        try:
            return self._decrypt(
                self.wallet_data['encryptedPrivateKey'],
                self.wallet_data['iv']
            )
        except Exception as e:
            logger.error(f"Failed to decrypt private key: {e}")
            return None

    def has_wallet(self) -> bool:
        """Check if a wallet exists."""
        return self.wallet_data is not None

    def get_balance(self) -> str:
        """
        Get the wallet balance in ETH.
        
        Returns:
            Balance as a string, "0" if error or no wallet
        """
        address = self.get_wallet_address()
        if not address:
            return "0"
            
        if not self.web3:
            logger.error("Web3 connection not available")
            return "0"
        
        try:
            balance_wei = self.web3.eth.get_balance(address)
            balance_eth = self.web3.from_wei(balance_wei, 'ether')
            return str(balance_eth)
        except Exception as e:
            logger.error(f"Failed to get balance: {e}")
            return "0"

    def delete_wallet(self) -> bool:
        """
        Delete the wallet and associated data.
        
        Returns:
            True if successful
        """
        try:
            if self.wallet_file.exists():
                self.wallet_file.unlink()
            
            # Try to delete password from keyring
            try:
                keyring.delete_password(self.SERVICE_NAME, self.PASSWORD_KEY)
            except keyring.errors.PasswordDeleteError:
                pass  # Password wasn't in keyring
            
            # Delete password file if it exists
            if self.password_file.exists():
                self.password_file.unlink()
            
            self.wallet_data = None
            self.password = None
            
            logger.info("Wallet and associated data deleted")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete wallet: {e}")
            return False

# ---------------------------------------------------------------------------
# Module-level singleton so that legacy imports like
# `from ..utils.wallet import wallet_manager` continue to work.
# ---------------------------------------------------------------------------

# Safe defaults – files will be created in the current working directory.
wallet_manager = WalletManager()

 