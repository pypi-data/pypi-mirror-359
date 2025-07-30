"""Tests for utility functions."""
import pytest
from yamleaf.utils import (
    get_nested_value, set_nested_value, delete_nested_value,
    flatten_dict, unflatten_dict, merge_configs, validate_config_structure
)


def test_get_nested_value():
    data = {'a': {'b': {'c': 42}}}
    assert get_nested_value(data, 'a.b.c') == 42
    assert get_nested_value(data, 'a.missing', 'default') == 'default'


def test_set_nested_value():
    data = {}
    set_nested_value(data, 'a.b.c', 42)
    assert data == {'a': {'b': {'c': 42}}}


def test_flatten_dict():
    data = {'a': {'b': 1}, 'c': [{'d': 2}]}
    result = flatten_dict(data)
    assert result['a.b'] == 1
    assert result['c[0].d'] == 2


def test_merge_configs():
    base = {'a': 1, 'b': {'c': 2}}
    override = {'b': {'d': 3}, 'e': 4}
    result = merge_configs(base, override)
    assert result == {'a': 1, 'b': {'c': 2, 'd': 3}, 'e': 4}
