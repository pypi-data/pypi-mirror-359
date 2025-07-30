# Solana Utils

A comprehensive toolkit for Solana blockchain development, wallet management, and network interaction.

## Features

- **Wallet Management**: Create, import, and manage Solana wallets
- **Transaction Utilities**: Build, sign, and send transactions
- **Network Tools**: Connect to different Solana networks (mainnet, testnet, devnet)
- **Token Management**: Create and manage SPL tokens
- **NFT Utilities**: Mint and manage NFTs on Solana

## Installation

```bash
pip install solana-sdkpy
```

## Quick Start

```python
from solana_utils import SolanaWallet, NetworkClient

# Create a new wallet
wallet = SolanaWallet.create()
print(f"New wallet address: {wallet.public_key}")

# Connect to Solana network
client = NetworkClient("devnet")

# Check wallet balance
balance = client.get_balance(wallet.public_key)
print(f"Wallet balance: {balance} SOL")
```

## Documentation

For detailed documentation and examples, visit our [documentation site](https://solana-utils.readthedocs.io/).

## Security

This package follows best practices for secure key management. Private keys are never stored in plaintext and are encrypted using industry-standard methods.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Solana Foundation for their excellent blockchain infrastructure
- The Python Solana community for their ongoing support 