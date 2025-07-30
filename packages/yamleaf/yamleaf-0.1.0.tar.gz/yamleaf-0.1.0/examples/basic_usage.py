"""
Basic usage examples for yamleaf.
"""

from yamleaf import ConfigManager


# Example 1: Basic usage with existing config file
def basic_example():
    # Load existing config with auto-save
    config = ConfigManager('config.yaml', auto_save=True, backup=True)

    # Dictionary-style access
    db_host = config['database.host']
    config['database.port'] = 5432

    # Attribute-style access
    api_key = config.api.key
    config.api.timeout = 30

    # Mixed access patterns
    config.logging.level = 'DEBUG'
    config['features.new_ui'] = True

    print(f"Database: {config.database.host}:{config.database.port}")
    print(f"API timeout: {config.api.timeout}")


# Example 2: Create config if missing
def create_config_example():
    default_config = {
        'app': {
            'name': 'MyApp',
            'version': '1.0.0',
            'debug': False
        },
        'database': {
            'host': 'localhost',
            'port': 5432
        }
    }

    config = ConfigManager(
        'new_config.yaml',
        create_if_missing=True,
        default_config=default_config,
        auto_save=True
    )

    # Modify configuration
    config.app.debug = True
    config.database.host = 'production-db.com'

    print(f"App: {config.app.name} v{config.app.version}")


# Example 3: Context manager usage
def context_manager_example():
    with ConfigManager('config.yaml') as config:
        config.temp_setting = 'temporary_value'
        config.app.maintenance_mode = True
        # Auto-saves on exit


if __name__ == '__main__':
    basic_example()
    create_config_example()
    context_manager_example()
