"""
GPUTOP - Real-time GPU monitoring tool
"""

from ._version import __version__, __package_name__
from .cli import main

__all__ = ["main", "__version__", "__package_name__"]
