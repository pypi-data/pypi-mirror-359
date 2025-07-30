"""
Custom exceptions for the yaml-config-manager package.
"""


class ConfigError(Exception):
    """Base exception for configuration errors."""
    pass


class ConfigNotFoundError(ConfigError):
    """Raised when configuration file is not found."""
    pass


class ConfigValidationError(ConfigError):
    """Raised when configuration validation fails."""
    pass


class ConfigParseError(ConfigError):
    """Raised when configuration file cannot be parsed."""
    pass


class ConfigPermissionError(ConfigError):
    """Raised when there are permission issues with config file operations."""
    pass
