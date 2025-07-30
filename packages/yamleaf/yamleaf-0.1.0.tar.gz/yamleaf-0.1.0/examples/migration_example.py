"""
Example showing migration from PyYAML to yamleaf.
"""

import yaml
from yamleaf import ConfigManager


def old_way():
    """Old way using PyYAML directly."""
    # Load config
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)

    # Access values
    db_host = config['database']['host']
    config['database']['port'] = 5432

    # Save config (loses formatting)
    with open('config.yaml', 'w') as f:
        yaml.dump(config, f)


def new_way():
    """New way using yamleaf."""
    # Load config (preserves formatting)
    config = ConfigManager('config.yaml', auto_save=True)

    # All old access patterns still work
    db_host = config['database']['host']  # Dictionary access
    config['database']['port'] = 5432  # Dictionary setting

    # Plus new access patterns
    db_host = config.database.host  # Attribute access
    config.database.port = 5432  # Attribute setting

    # Auto-saves with preserved formatting!


def gradual_migration():
    """Gradual migration strategy."""
    config = ConfigManager('config.yaml')

    # Start with dictionary access (no changes needed)
    db_config = config['database']

    # Gradually adopt attribute access for new code
    config.new_feature = {'enabled': True}
    config.new_feature.settings = {'timeout': 30}

    # Mix approaches as needed
    config['legacy_setting'] = 'value'
    config.modern_setting = 'value'


if __name__ == '__main__':
    print("Migration examples:")
    print("1. Old PyYAML way")
    old_way()

    print("2. New yamleaf way")
    new_way()

    print("3. Gradual migration approach")
    gradual_migration()
