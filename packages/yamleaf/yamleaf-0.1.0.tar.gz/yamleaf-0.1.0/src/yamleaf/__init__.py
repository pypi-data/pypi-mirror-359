"""
Yamleaf

A Python package for managing YAML configuration files while preserving
structure, comments, and formatting. Supports both dictionary and attribute
access patterns with optional type validation.
"""

from .config_manager import ConfigManager, TypedConfigManager, ConfigProxy
from .exceptions import ConfigError, ConfigNotFoundError, ConfigValidationError
from .types import ConfigProtocol, DatabaseConfig, APIConfig, LoggingConfig, AppConfig
from .utils import get_nested_value, set_nested_value, flatten_dict

__version__ = "0.1.0"
__all__ = [
    "ConfigManager",
    "TypedConfigManager",
    "ConfigProxy",
    "ConfigError",
    "ConfigNotFoundError",
    "ConfigValidationError",
    "ConfigProtocol",
    "DatabaseConfig",
    "APIConfig",
    "LoggingConfig",
    "AppConfig",
    "get_nested_value",
    "set_nested_value",
    "flatten_dict"
]
