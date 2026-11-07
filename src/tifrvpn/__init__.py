"""TIFR VPN library and command-line tools.

Importing the package performs no credential, network, or GUI operations.
"""

from .config import Config, load_config
from .errors import VPNError
from .vpn import VPNStatus, connect, disconnect, forget_login, setup, status

__all__ = [
    "Config",
    "VPNError",
    "VPNStatus",
    "connect",
    "disconnect",
    "forget_login",
    "load_config",
    "setup",
    "status",
]
