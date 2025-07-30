"""
Typed usage examples with validation.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional
from yamleaf import ConfigManager


@dataclass
class DatabaseConfig:
    host: str = "localhost"
    port: int = 5432
    name: str = "myapp"
    ssl: bool = False


@dataclass
class APIConfig:
    base_url: str = "https://api.example.com"
    timeout: int = 30
    retries: int = 3
    headers: Dict[str, str] = None


@dataclass
class AppConfig:
    name: str
    version: str
    debug: bool
    database: DatabaseConfig
    api: APIConfig


def typed_config_example():
    """Example with type validation."""
    config = ConfigManager(
        'typed_config.yaml',
        config_class=AppConfig,
        validate_types=True,
        auto_save=True
    )

    # Type validation and conversion
    config.database.port = "3306"  # Converted to int
    config.debug = "false"  # Converted to bool

    # Access with full IDE support
    print(f"App: {config.name}")
    print(f"Database: {config.database.host}:{config.database.port}")
    print(f"Debug mode: {config.debug}")


def partial_typing_example():
    """Example with partial typing for existing configs."""

    @dataclass
    class PartialConfig:
        # Only type the fields you care about
        database_host: str
        api_timeout: int
        debug_mode: bool

    config = ConfigManager(
        'existing_config.yaml',
        config_class=PartialConfig,
        validate_types=True
    )

    # Only specified fields are type-validated
    config.database_host = "new-host.com"
    config.api_timeout = 45

    # Other fields remain flexible
    config.some_other_setting = {"flexible": "value"}


if __name__ == '__main__':
    typed_config_example()
    partial_typing_example()
