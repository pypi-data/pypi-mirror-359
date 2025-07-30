"""
GPUTOP - Real-time GPU monitoring tool
"""

__version__ = "0.1.7"
__package_name__ = "GPUTOP"

from .cli import main

__all__ = ["main", "__version__", "__package_name__"]
