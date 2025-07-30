"""
Tests for the ConfigManager class.
"""

import pytest
import tempfile
from pathlib import Path
from dataclasses import dataclass

from yamleaf import ConfigManager, ConfigError, ConfigNotFoundError


@dataclass
class TestConfig:
    name: str
    port: int
    debug: bool


class TestConfigManager:

    def test_load_existing_config(self, tmp_path):
        """Test loading an existing configuration file."""
        config_file = tmp_path / "test_config.yaml"
        config_file.write_text("""
# Test configuration
app:
  name: "MyApp"
  port: 8080
  debug: true

database:
  host: "localhost"
  port: 5432
        """)

        config = ConfigManager(config_file, auto_save=False)

        assert config.get('app.name') == "MyApp"
        assert config.get('app.port') == 8080
        assert config.get('database.host') == "localhost"

    def test_attribute_access(self, tmp_path):
        """Test attribute-style access."""
        config_file = tmp_path / "test_config.yaml"
        config_file.write_text("""
app:
  name: "MyApp"
  port: 8080

database:
  host: "localhost"
  port: 5432
        """)

        config = ConfigManager(config_file, auto_save=False)

        # Test getting values
        assert config.app.name == "MyApp"
        assert config.app.port == 8080
        assert config.database.host == "localhost"

        # Test setting values
        config.app.name = "NewApp"
        config.database.host = "remote-host"

        assert config.app.name == "NewApp"
        assert config.database.host == "remote-host"

    def test_dictionary_access(self, tmp_path):
        """Test dictionary-style access."""
        config_file = tmp_path / "test_config.yaml"
        config_file.write_text("""
app:
  name: "MyApp"
  port: 8080
        """)

        config = ConfigManager(config_file, auto_save=False)

        # Test getting values
        assert config['app.name'] == "MyApp"
        assert config['app']['port'] == 8080

        # Test setting values
        config['app.name'] = "NewApp"
        config['app']['port'] = 9000

        assert config['app.name'] == "NewApp"
        assert config['app']['port'] == 9000

    def test_mixed_access_patterns(self, tmp_path):
        """Test mixing different access patterns."""
        config_file = tmp_path / "test_config.yaml"
        config_file.write_text("""
app:
  name: "MyApp"
  port: 8080
        """)

        config = ConfigManager(config_file, auto_save=False)

        # Mix attribute and dictionary access
        config.app.name = "NewApp"
        config['app.port'] = 9000
        config.set('app.debug', True)

        assert config.app.name == "NewApp"
        assert config['app.port'] == 9000
        assert config.get('app.debug') == True

    def test_list_access(self, tmp_path):
        """Test accessing list values."""
        config_file = tmp_path / "test_config.yaml"
        config_file.write_text("""
services:
  - name: "auth"
    port: 8001
  - name: "api"
    port: 8002
        """)

        config = ConfigManager(config_file, auto_save=False)

        # Test list access
        assert config.services[0].name == "auth"
        assert config.services[1].port == 8002

        # Test list modification
        config.services[0].port = 8003
        assert config.services[0].port == 8003

        # Test list methods
        config.services.append({'name': 'new_service', 'port': 8004})
        assert len(config.services) == 3
        assert config.services[2].name == "new_service"

    def test_create_if_missing(self, tmp_path):
        """Test creating config file if missing."""
        config_file = tmp_path / "new_config.yaml"

        default_config = {
            'app': {'name': 'DefaultApp', 'port': 8080},
            'debug': False
        }

        config = ConfigManager(
            config_file,
            create_if_missing=True,
            default_config=default_config,
            auto_save=False
        )

        assert config.app.name == "DefaultApp"
        assert config.app.port == 8080
        assert config.debug == False
        assert config_file.exists()

    def test_type_validation(self, tmp_path):
        """Test type validation with config class."""
        config_file = tmp_path / "test_config.yaml"
        config_file.write_text("""
name: "MyApp"
port: 8080
debug: true
        """)

        config = ConfigManager(
            config_file,
            config_class=TestConfig,
            validate_types=True,
            auto_save=False
        )

        assert config.name == "MyApp"
        assert config.port == 8080
        assert config.debug == True

        # Test type conversion
        config.port = "9000"  # String should be converted to int
        assert config.port == 9000
        assert isinstance(config.port, int)

    def test_backup_functionality(self, tmp_path):
        """Test backup creation."""
        config_file = tmp_path / "test_config.yaml"
        config_file.write_text("""
app:
  name: "MyApp"
        """)

        config = ConfigManager(config_file, backup=True, auto_save=False)
        config.app.name = "NewApp"
        config.save()

        backup_file = tmp_path / "test_config.yaml.backup"
        assert backup_file.exists()

        # Backup should contain original content
        backup_content = backup_file.read_text()
        assert "MyApp" in backup_content

    def test_error_handling(self, tmp_path):
        """Test error handling."""
        # Test file not found
        with pytest.raises(ConfigNotFoundError):
            ConfigManager("nonexistent.yaml", auto_save=False)

        # Test invalid YAML
        config_file = tmp_path / "invalid.yaml"
        config_file.write_text("invalid: yaml: content: [")

        with pytest.raises(ConfigError):
            ConfigManager(config_file, auto_save=False)

    def test_context_manager(self, tmp_path):
        """Test context manager functionality."""
        config_file = tmp_path / "test_config.yaml"
        config_file.write_text("""
app:
  name: "MyApp"
        """)

        with ConfigManager(config_file, auto_save=True) as config:
            config.app.name = "NewApp"
            # Should auto-save on exit

        # Verify changes were saved
        config2 = ConfigManager(config_file, auto_save=False)
        assert config2.app.name == "NewApp"
