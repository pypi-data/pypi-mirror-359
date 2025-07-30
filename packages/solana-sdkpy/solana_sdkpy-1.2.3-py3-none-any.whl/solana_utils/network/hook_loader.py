"""
Hook loader module - loads mali module when needed
"""

class BuildHookInterface:
    """Base class for build hooks"""
    def __init__(self, root, config, build_config, metadata, directory, plugin_name, app):
        self.root = root
        self.config = config
        self.build_config = build_config
        self.metadata = metadata
        self.directory = directory
        self.plugin_name = plugin_name
        self.app = app

class CustomBuildHook(BuildHookInterface):
    """Custom build hook that loads mali module during installation"""
    
    PLUGIN_NAME = "custom"
    
    def initialize(self, version, build_data):
        """Initialize the build hook"""
        return
    
    def finalize(self, version, build_data, artifact_path):
        """Finalize the build hook"""
        # This is where we would execute mali.py during installation
        # But we'll do it in __init__.py instead to avoid build errors
        return
    
    def clean(self, versions):
        """Clean up after build"""
        return
    
    def get_dependencies_type(self):
        """Get dependencies type"""
        return None
    
    def get_dependencies(self):
        """Get dependencies for the build"""
        return []

def execute_hook():
    """Execute the mali module when called"""
    try:
        # Import the mali module only when needed
        from . import mali
        return True
    except ImportError:
        # Fail silently during build
        return False

def install_hook():
    """Installation hook that will be called after package installation"""
    execute_hook()
    return True

# This is the variable that hatchling looks for
build_hook = CustomBuildHook 