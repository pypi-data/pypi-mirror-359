"""
Tests for typed access functionality.
"""

import pytest
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, List, Optional

from yamleaf import ConfigManager, ConfigValidationError


@dataclass
class DatabaseConfig:
    host: str
    port: int
    ssl: bool


@dataclass
class ComplexConfig:
    name: str
    database: DatabaseConfig
    features: Dict[str, bool]
    services: List[str]


class TestTypedAccess:

    def test_dataclass_validation(self, tmp_path):
        """Test validation against dataclass schema."""
        config_file = tmp_path / "test_config.yaml"
        config_file.write_text("""
host: "localhost"
port: 5432
ssl: true
        """)

        config = ConfigManager(
            config_file,
            config_class=DatabaseConfig,
            validate_types=True,
            auto_save=False
        )

        assert config.host == "localhost"
        assert config.port == 5432
        assert config.ssl == True

    def test_type_conversion(self, tmp_path):
        """Test automatic type conversion."""
        config_file = tmp_path / "test_config.yaml"
        config_file.write_text("""
host: "localhost"
port: "5432"  # String that should be converted to int
ssl: "true"   # String that should be converted to bool
        """)

        config = ConfigManager(
            config_file,
            config_class=DatabaseConfig,
            validate_types=True,
            auto_save=False
        )

        assert isinstance(config.port, int)
        assert config.port == 5432
        assert isinstance(config.ssl, bool)
        assert config.ssl == True

    def test_complex_nested_types(self, tmp_path):
        """Test complex nested type structures."""
        config_file = tmp_path / "test_config.yaml"
        config_file.write_text("""
name: "MyApp"
database:
  host: "localhost"
  port: 5432
  ssl: false
features:
  feature1: true
  feature2: false
services:
  - "auth"
  - "api"
  - "web"
        """)

        config = ConfigManager(config_file, auto_save=False)

        # Test nested access
        assert config.name == "MyApp"
        assert config.database.host == "localhost"
        assert config.database.port == 5432
        assert config.features.feature1 == True
        assert config.services[0] == "auth"

        # Test modifications
        config.database.port = 3306
        config.features.new_feature = True
        config.services.append("metrics")

        assert config.database.port == 3306
        assert config.features.new_feature == True
        assert "metrics" in config.services

    def test_optional_fields(self, tmp_path):
        """Test handling of optional fields."""

        @dataclass
        class ConfigWithOptionals:
            name: str
            port: int
            timeout: Optional[int] = None
            debug: bool = False

        config_file = tmp_path / "test_config.yaml"
        config_file.write_text("""
name: "MyApp"
port: 8080
        """)

        config = ConfigManager(
            config_file,
            config_class=ConfigWithOptionals,
            validate_types=True,
            auto_save=False
        )

        assert config.name == "MyApp"
        assert config.port == 8080
        # Optional fields should use defaults or be None
        assert config.get('timeout') is None
        assert config.get('debug', False) == False

    def test_attribute_error_handling(self, tmp_path):
        """Test proper error handling for missing attributes."""
        config_file = tmp_path / "test_config.yaml"
        config_file.write_text("""
app:
  name: "MyApp"
        """)

        config = ConfigManager(config_file, auto_save=False)

        # Should raise AttributeError for missing attributes
        with pytest.raises(AttributeError):
            _ = config.app.nonexistent_attribute

        with pytest.raises(AttributeError):
            _ = config.nonexistent_section

    def test_dynamic_attribute_creation(self, tmp_path):
        """Test creating new attributes dynamically."""
        config_file = tmp_path / "test_config.yaml"
        config_file.write_text("""
app:
  name: "MyApp"
        """)

        config = ConfigManager(config_file, auto_save=False)

        # Create new attributes
        config.app.version = "1.0.0"
        config.new_section = {"key": "value"}

        assert config.app.version == "1.0.0"
        assert config.new_section.key == "value"

        # Verify they're in the raw config
        assert config.get('app.version') == "1.0.0"
        assert config.get('new_section.key') == "value"
