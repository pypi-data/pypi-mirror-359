from pathlib import Path
from typing import Any, Dict, Optional, Union, TypeVar, Generic, get_type_hints
import atexit
from ruamel.yaml import YAML

from .exceptions import ConfigError, ConfigNotFoundError, ConfigValidationError
from .utils import get_nested_value, set_nested_value

T = TypeVar('T')


class ConfigProxy:
    """
    A proxy object that provides attribute-style access to nested config values.
    Maintains references to the original data and config manager for live updates.
    """

    def __init__(self, data: Dict[str, Any], parent_path: str = '', config_manager: 'ConfigManager' = None):
        object.__setattr__(self, '_data', data)
        object.__setattr__(self, '_parent_path', parent_path)
        object.__setattr__(self, '_config_manager', config_manager)
        object.__setattr__(self, '_list_parent', None)
        object.__setattr__(self, '_list_index', None)

    def __getattr__(self, name: str) -> Any:
        if name.startswith('_'):
            return object.__getattribute__(self, name)

        if name not in self._data:
            raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")

        value = self._data[name]
        current_path = f"{self._parent_path}.{name}" if self._parent_path else name

        if isinstance(value, dict):
            proxy = ConfigProxy(value, current_path, self._config_manager)
            return proxy
        elif isinstance(value, list):
            return ConfigListProxy(value, current_path, self._config_manager)
        return value

    def __setattr__(self, name: str, value: Any) -> None:
        if name.startswith('_'):
            object.__setattr__(self, name, value)
            return

        current_path = f"{self._parent_path}.{name}" if self._parent_path else name

        # Check if this is a list item proxy
        if hasattr(self, '_list_parent') and self._list_parent is not None:
            # For list items, update the data directly and sync with list
            self._data[name] = value
            # Update the actual list data
            self._list_parent._data[self._list_index] = self._data
            # Mark config as modified
            if self._config_manager:
                self._config_manager._modified = True
        else:
            # For direct config children, use set method for type validation
            if self._config_manager:
                self._config_manager.set(current_path, value)
            else:
                # Fallback for proxies without config manager
                self._data[name] = value

    def __getitem__(self, key: str) -> Any:
        return self.__getattr__(key)

    def __setitem__(self, key: str, value: Any) -> None:
        self.__setattr__(key, value)

    def __contains__(self, key: str) -> bool:
        return key in self._data

    def __repr__(self) -> str:
        return f"ConfigProxy({self._data})"

    def __str__(self) -> str:
        return str(self._data)

    def __dir__(self):
        # Support for IDE autocompletion
        return list(self._data.keys()) + ['to_dict', 'keys', 'values', 'items']

    def keys(self):
        return self._data.keys()

    def values(self):
        for key, value in self._data.items():
            if isinstance(value, dict):
                yield ConfigProxy(value, f"{self._parent_path}.{key}" if self._parent_path else key,
                                  self._config_manager)
            elif isinstance(value, list):
                yield ConfigListProxy(value, f"{self._parent_path}.{key}" if self._parent_path else key,
                                      self._config_manager)
            else:
                yield value

    def items(self):
        for key, value in self._data.items():
            if isinstance(value, dict):
                yield key, ConfigProxy(value, f"{self._parent_path}.{key}" if self._parent_path else key,
                                       self._config_manager)
            elif isinstance(value, list):
                yield key, ConfigListProxy(value, f"{self._parent_path}.{key}" if self._parent_path else key,
                                           self._config_manager)
            else:
                yield key, value

    def to_dict(self) -> Dict[str, Any]:
        """Convert proxy back to plain dictionary."""
        result = {}
        for key, value in self._data.items():
            if isinstance(value, dict):
                result[key] = ConfigProxy(value).to_dict()
            elif isinstance(value, list):
                result[key] = list(value)
            else:
                result[key] = value
        return result


class ConfigListProxy:
    """
    A proxy object for list values in configuration.
    """

    def __init__(self, data: list, parent_path: str = '', config_manager: 'ConfigManager' = None):
        object.__setattr__(self, '_data', data)
        object.__setattr__(self, '_parent_path', parent_path)
        object.__setattr__(self, '_config_manager', config_manager)
        object.__setattr__(self, '_item_proxies', {})  # Cache for item proxies

    def __getitem__(self, index: int) -> Any:
        value = self._data[index]
        if isinstance(value, dict):
            # Return cached proxy or create new one
            if index not in self._item_proxies:
                current_path = f"{self._parent_path}[{index}]"
                proxy = ConfigProxy(value, current_path, self._config_manager)
                # Store reference to update the list when proxy changes
                object.__setattr__(proxy, '_list_parent', self)
                object.__setattr__(proxy, '_list_index', index)
                self._item_proxies[index] = proxy
            return self._item_proxies[index]
        return value

    def __setitem__(self, index: int, value: Any) -> None:
        self._data[index] = value
        # Clear cached proxy for this index
        if index in self._item_proxies:
            del self._item_proxies[index]
        if self._config_manager:
            self._config_manager._modified = True

    def __len__(self) -> int:
        return len(self._data)

    def __iter__(self):
        for i, item in enumerate(self._data):
            if isinstance(item, dict):
                # Use __getitem__ to get consistent proxy behavior
                yield self[i]
            else:
                yield item

    def append(self, value: Any) -> None:
        self._data.append(value)
        if self._config_manager:
            self._config_manager._modified = True

    def extend(self, values: list) -> None:
        self._data.extend(values)
        if self._config_manager:
            self._config_manager._modified = True

    def insert(self, index: int, value: Any) -> None:
        self._data.insert(index, value)
        # Shift cached proxies
        new_proxies = {}
        for i, proxy in self._item_proxies.items():
            if i >= index:
                object.__setattr__(proxy, '_list_index', i + 1)
                new_proxies[i + 1] = proxy
            else:
                new_proxies[i] = proxy
        self._item_proxies = new_proxies
        if self._config_manager:
            self._config_manager._modified = True

    def remove(self, value: Any) -> None:
        index = self._data.index(value)
        self._data.remove(value)
        # Remove and shift cached proxies
        if index in self._item_proxies:
            del self._item_proxies[index]
        new_proxies = {}
        for i, proxy in self._item_proxies.items():
            if i > index:
                object.__setattr__(proxy, '_list_index', i - 1)
                new_proxies[i - 1] = proxy
            elif i < index:
                new_proxies[i] = proxy
        self._item_proxies = new_proxies
        if self._config_manager:
            self._config_manager._modified = True

    def pop(self, index: int = -1) -> Any:
        if index == -1:
            index = len(self._data) - 1
        result = self._data.pop(index)
        # Remove and shift cached proxies
        if index in self._item_proxies:
            del self._item_proxies[index]
        new_proxies = {}
        for i, proxy in self._item_proxies.items():
            if i > index:
                object.__setattr__(proxy, '_list_index', i - 1)
                new_proxies[i - 1] = proxy
            elif i < index:
                new_proxies[i] = proxy
        self._item_proxies = new_proxies
        if self._config_manager:
            self._config_manager._modified = True
        return result

    def __repr__(self) -> str:
        return f"ConfigListProxy({self._data})"

    def __str__(self) -> str:
        return str(self._data)


class TypedConfigManager(Generic[T]):
    """
    A typed configuration manager that provides both dictionary and attribute access.
    Preserves YAML structure, comments, and formatting while offering modern Python access patterns.
    """

    def __init__(
            self,
            config_path: Union[str, Path],
            config_class: Optional[type] = None,
            auto_save: bool = True,
            backup: bool = False,
            indent: int = 2,
            sequence_indent: int = 4,
            validate_types: bool = True,
            create_if_missing: bool = False,
            default_config: Optional[Dict[str, Any]] = None
    ):
        self.config_path = Path(config_path)
        self.config_class = config_class
        self.auto_save = auto_save
        self.backup = backup
        self.validate_types = validate_types
        self.create_if_missing = create_if_missing
        self.default_config = default_config or {}
        self._modified = False
        self._type_hints = {}

        # Handle missing config file
        if not self.config_path.exists():
            if create_if_missing:
                self._create_default_config()
            else:
                raise ConfigNotFoundError(f"Config file not found: {self.config_path}")

        # Get type hints if config class is provided
        if config_class:
            try:
                self._type_hints = get_type_hints(config_class)
            except (NameError, AttributeError):
                # Handle forward references or missing imports
                self._type_hints = getattr(config_class, '__annotations__', {})

        # Initialize YAML handler
        self.yaml = YAML()
        self.yaml.preserve_quotes = True
        self.yaml.map_indent = indent
        self.yaml.sequence_indent = sequence_indent
        self.yaml.width = 4096  # Prevent line wrapping

        # Load configuration
        self._load_config()

        # Register cleanup
        if auto_save:
            atexit.register(self.save)

    def _create_default_config(self) -> None:
        """Create a default configuration file."""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)

        yaml = YAML()
        yaml.preserve_quotes = True
        yaml.map_indent = 2
        yaml.sequence_indent = 4

        with open(self.config_path, 'w', encoding='utf-8') as f:
            yaml.dump(self.default_config, f)

    def _load_config(self) -> None:
        """Load configuration from file."""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                raw_config = self.yaml.load(f)

            # Handle empty or None config
            if raw_config is None:
                raw_config = {}

            self._raw_config = raw_config
            self._config_proxy = ConfigProxy(raw_config, config_manager=self)

            # Validate types if enabled and type hints available
            if self.validate_types and self._type_hints:
                self._validate_config()

        except Exception as e:
            raise ConfigError(f"Failed to load config: {e}")

    def _validate_config(self) -> None:
        """Validate configuration against type hints."""
        for key, expected_type in self._type_hints.items():
            if key in self._raw_config:
                value = self._raw_config[key]
                if not self._is_valid_type(value, expected_type):
                    # Try to convert basic types
                    converted_value = self._convert_type(value, expected_type)
                    if converted_value is not None:
                        self._raw_config[key] = converted_value
                        # Update the proxy as well
                        self._config_proxy._data[key] = converted_value
                    else:
                        raise ConfigValidationError(
                            f"Config key '{key}' expected {expected_type}, "
                            f"got {type(value).__name__}: {value}"
                        )

    def _is_valid_type(self, value: Any, expected_type: type) -> bool:
        """Check if value matches expected type."""
        # Handle Union types and Optional
        if hasattr(expected_type, '__origin__'):
            if expected_type.__origin__ is Union:
                return any(self._is_valid_type(value, arg) for arg in expected_type.__args__)

        # Handle basic type checking
        if expected_type in (int, float, str, bool, list, dict):
            return isinstance(value, expected_type)

        return isinstance(value, expected_type)

    def _convert_type(self, value: Any, expected_type: type) -> Optional[Any]:
        """Try to convert value to expected type."""
        try:
            if expected_type == int:
                return int(value)
            elif expected_type == float:
                return float(value)
            elif expected_type == bool:
                if isinstance(value, str):
                    return value.lower() in ('true', '1', 'yes', 'on')
                return bool(value)
            elif expected_type == str:
                return str(value)
            elif expected_type == list and not isinstance(value, list):
                return [value]
        except (ValueError, TypeError):
            pass
        return None

    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Get a configuration value using dot notation.

        Args:
            key_path: Dot-separated path to the value (e.g., 'database.host')
            default: Default value if key not found

        Returns:
            The configuration value or default
        """
        return get_nested_value(self._raw_config, key_path, default)

    def set(self, key_path: str, value: Any) -> None:
        """
        Set a configuration value using dot notation.

        Args:
            key_path: Dot-separated path to the value
            value: Value to set
        """
        # Type validation for top-level keys
        if self.validate_types and self._type_hints:
            top_key = key_path.split('.')[0]
            if top_key in self._type_hints:
                expected_type = self._type_hints[top_key]
                if not self._is_valid_type(value, expected_type):
                    converted_value = self._convert_type(value, expected_type)
                    if converted_value is not None:
                        value = converted_value
                    else:
                        raise ConfigValidationError(
                            f"Config key '{top_key}' expected {expected_type}, "
                            f"got {type(value).__name__}: {value}"
                        )

        set_nested_value(self._raw_config, key_path, value)
        # Also update the proxy data to keep it in sync
        set_nested_value(self._config_proxy._data, key_path, value)
        self._modified = True

    def update(self, updates: Dict[str, Any]) -> None:
        """
        Update multiple configuration values.

        Args:
            updates: Dictionary of key_path -> value mappings
        """
        for key_path, value in updates.items():
            self.set(key_path, value)

    def delete(self, key_path: str) -> None:
        """
        Delete a configuration key using dot notation.

        Args:
            key_path: Dot-separated path to the key to delete
        """
        keys = key_path.split('.')
        current = self._raw_config

        for key in keys[:-1]:
            if key not in current:
                return  # Key doesn't exist
            current = current[key]

        if keys[-1] in current:
            del current[keys[-1]]
            self._modified = True

    def save(self, path: Optional[Union[str, Path]] = None) -> None:
        """
        Save configuration to file.

        Args:
            path: Optional path to save to (defaults to original path)
        """
        if not self._modified and path is None:
            return

        save_path = Path(path) if path else self.config_path

        # Create backup if requested
        if self.backup and save_path.exists():
            backup_path = save_path.with_suffix(f'{save_path.suffix}.backup')
            backup_path.write_text(save_path.read_text(encoding='utf-8'), encoding='utf-8')

        try:
            # Ensure directory exists
            save_path.parent.mkdir(parents=True, exist_ok=True)

            with open(save_path, 'w', encoding='utf-8') as f:
                self.yaml.dump(self._raw_config, f)
            self._modified = False
        except Exception as e:
            raise ConfigError(f"Failed to save config: {e}")

    def reload(self) -> None:
        """Reload configuration from file, discarding changes."""
        self._load_config()
        self._modified = False

    def reset(self) -> None:
        """Reset configuration to default values."""
        self._raw_config = dict(self.default_config)
        self._config_proxy = ConfigProxy(self._raw_config, config_manager=self)
        self._modified = True

    @property
    def config(self) -> ConfigProxy:
        """Get the configuration proxy for attribute access."""
        return self._config_proxy

    @property
    def is_modified(self) -> bool:
        """Check if configuration has been modified."""
        return self._modified

    @property
    def raw_config(self) -> Dict[str, Any]:
        """Get the raw configuration dictionary."""
        return self._raw_config

    # Dictionary-style access
    def __getitem__(self, key: str) -> Any:
        return self.get(key)

    def __setitem__(self, key: str, value: Any) -> None:
        self.set(key, value)

    def __delitem__(self, key: str) -> None:
        self.delete(key)

    def __contains__(self, key: str) -> bool:
        try:
            self.get(key)
            return True
        except:
            return False

    def __len__(self) -> int:
        return len(self._raw_config)

    def __iter__(self):
        return iter(self._raw_config)

    def keys(self):
        return self._raw_config.keys()

    def values(self):
        return self._raw_config.values()

    def items(self):
        return self._raw_config.items()

    # Attribute-style access (delegated to config proxy)
    def __getattr__(self, name: str) -> Any:
        if name.startswith('_') or name in [
            'config', 'yaml', 'config_path', 'config_class', 'auto_save',
            'backup', 'validate_types', 'create_if_missing', 'default_config'
        ]:
            return object.__getattribute__(self, name)
        return getattr(self._config_proxy, name)

    def __setattr__(self, name: str, value: Any) -> None:
        if name.startswith('_') or name in [
            'config_path', 'config_class', 'auto_save', 'backup',
            'validate_types', 'create_if_missing', 'default_config', 'yaml'
        ]:
            object.__setattr__(self, name, value)
        else:
            # Use the set() method which includes type validation
            self.set(name, value)

    def __dir__(self):
        # Support for IDE autocompletion
        config_keys = list(self._raw_config.keys()) if self._raw_config else []
        manager_attrs = [
            'config', 'get', 'set', 'update', 'delete', 'save', 'reload', 'reset',
            'is_modified', 'raw_config', 'keys', 'values', 'items'
        ]
        return config_keys + manager_attrs

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.auto_save:
            self.save()


# Convenience alias
ConfigManager = TypedConfigManager
