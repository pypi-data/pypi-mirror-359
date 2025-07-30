"""
Utility functions for configuration management.
"""

from typing import Any, Dict, List, Union


def get_nested_value(data: Dict[str, Any], key_path: str, default: Any = None) -> Any:
    """
    Get a nested value using dot notation.

    Args:
        data: Dictionary to search in
        key_path: Dot-separated path to the value
        default: Default value if key not found

    Returns:
        The value at the specified path or default
    """
    if not key_path:
        return data

    keys = key_path.split('.')
    current = data

    try:
        for key in keys:
            # Handle list indices
            if isinstance(current, list) and key.isdigit():
                current = current[int(key)]
            elif isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return default
        return current
    except (KeyError, TypeError, IndexError, ValueError):
        return default


def set_nested_value(data: Dict[str, Any], key_path: str, value: Any) -> None:
    """
    Set a nested value using dot notation.

    Args:
        data: Dictionary to modify
        key_path: Dot-separated path to the value
        value: Value to set
    """
    if not key_path:
        return

    keys = key_path.split('.')
    current = data

    for key in keys[:-1]:
        if key not in current:
            current[key] = {}
        elif not isinstance(current[key], dict):
            # If the key exists but isn't a dict, replace it
            current[key] = {}
        current = current[key]

    current[keys[-1]] = value


def delete_nested_value(data: Dict[str, Any], key_path: str) -> bool:
    """
    Delete a nested value using dot notation.

    Args:
        data: Dictionary to modify
        key_path: Dot-separated path to the value to delete

    Returns:
        True if value was deleted, False if key didn't exist
    """
    if not key_path:
        return False

    keys = key_path.split('.')
    current = data

    try:
        for key in keys[:-1]:
            current = current[key]

        if keys[-1] in current:
            del current[keys[-1]]
            return True
        return False
    except (KeyError, TypeError):
        return False


def flatten_dict(data: Dict[str, Any], parent_key: str = '', sep: str = '.') -> Dict[str, Any]:
    """
    Flatten a nested dictionary using dot notation.

    Args:
        data: Dictionary to flatten
        parent_key: Parent key prefix
        sep: Separator for keys

    Returns:
        Flattened dictionary
    """
    items = []
    for key, value in data.items():
        new_key = f"{parent_key}{sep}{key}" if parent_key else key
        if isinstance(value, dict):
            items.extend(flatten_dict(value, new_key, sep=sep).items())
        elif isinstance(value, list):
            for i, item in enumerate(value):
                if isinstance(item, dict):
                    items.extend(flatten_dict(item, f"{new_key}[{i}]", sep=sep).items())
                else:
                    items.append((f"{new_key}[{i}]", item))
        else:
            items.append((new_key, value))
    return dict(items)


def unflatten_dict(data: Dict[str, Any], sep: str = '.') -> Dict[str, Any]:
    """
    Unflatten a dictionary from dot notation back to nested structure.

    Args:
        data: Flattened dictionary
        sep: Separator used in keys

    Returns:
        Nested dictionary
    """
    result = {}
    for key, value in data.items():
        set_nested_value(result, key, value)
    return result


def merge_configs(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    """
    Deep merge two configuration dictionaries.

    Args:
        base: Base configuration
        override: Configuration to merge in

    Returns:
        Merged configuration
    """
    result = base.copy()

    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_configs(result[key], value)
        else:
            result[key] = value

    return result


def validate_config_structure(config: Dict[str, Any], schema: Dict[str, type]) -> List[str]:
    """
    Validate configuration structure against a schema.

    Args:
        config: Configuration to validate
        schema: Schema dictionary with expected types

    Returns:
        List of validation errors
    """
    errors = []

    for key, expected_type in schema.items():
        if key not in config:
            errors.append(f"Missing required key: {key}")
        elif not isinstance(config[key], expected_type):
            errors.append(f"Key '{key}' expected {expected_type.__name__}, got {type(config[key]).__name__}")

    return errors


def sanitize_key(key: str) -> str:
    """
    Sanitize a configuration key to ensure it's valid.

    Args:
        key: Key to sanitize

    Returns:
        Sanitized key
    """
    # Remove invalid characters and normalize
    sanitized = ''.join(c for c in key if c.isalnum() or c in '._-')

    # Ensure it doesn't start with a number
    if sanitized and sanitized[0].isdigit():
        sanitized = f"_{sanitized}"

    return sanitized
