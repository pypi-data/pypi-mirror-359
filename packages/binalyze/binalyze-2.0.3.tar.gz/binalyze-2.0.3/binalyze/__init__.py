"""
Binalyze SDK Package

A comprehensive Python SDK package for Binalyze products.
Future-proofed to support AIR, Fleet, and other Binalyze solutions.
"""

__version__ = "2.0.0"

# Re-export from air subpackage for backwards compatibility
from .air import (
    sdk,
    SDK,
    create_sdk,
    create_sdk_from_env,
    create_sdk_with_debug,
    create_sdk_with_verbose
)

__all__ = [
    "sdk",
    "SDK",
    "create_sdk",
    "create_sdk_from_env",
    "create_sdk_with_debug",
    "create_sdk_with_verbose",
] 