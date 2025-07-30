"""
TGLib is an open-source temporal graph library focusing on temporal distance and centrality computations, and other local and global temporal graph statistics.
"""

try:
    from .pytglib import *
except ImportError as e:
    import sys
    import platform
    
    # Provide helpful error message
    arch = platform.machine()
    system = platform.system()
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}"
    
    raise ImportError(
        f"Failed to import tglib native module. "
        f"This could be due to:\n"
        f"1. Missing dependencies\n"
        f"2. Incompatible architecture ({system} {arch})\n"
        f"3. Python version mismatch (using {python_version})\n"
        f"Original error: {e}"
    ) from e

__version__ = "0.1.0"  # Will be replaced by setuptools_scm
