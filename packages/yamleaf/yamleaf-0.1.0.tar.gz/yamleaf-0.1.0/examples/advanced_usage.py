"""
Advanced usage examples for complex scenarios.
"""

from yamleaf import ConfigManager
from yamleaf.types import AppConfig, ServiceConfig
from yamleaf.utils import merge_configs, flatten_dict


def microservices_example():
    """Managing microservices configuration."""
    config = ConfigManager('services_config.yaml', auto_save=True)

    # Access service configurations
    for i, service in enumerate(config.services):
        print(f"Service: {service.name} on port {service.port}")

        # Update service config
        if service.name == "auth_service":
            service.endpoints.append("/oauth")
            service.resources.cpu = "500m"
            service.resources.memory = "512Mi"

    # Add new service
    new_service = {
        'name': 'metrics_service',
        'port': 9090,
        'endpoints': ['/metrics', '/health'],
        'enabled': True
    }
    config.services.append(new_service)


def environment_specific_configs():
    """Managing environment-specific configurations."""
    # Base config
    base_config = ConfigManager('base_config.yaml', auto_save=False)

    # Environment overrides
    env_config = ConfigManager('production_config.yaml', auto_save=False)

    # Merge configurations
    merged = merge_configs(base_config.raw_config, env_config.raw_config)

    # Create final config
    final_config = ConfigManager(
        'final_config.yaml',
        create_if_missing=True,
        default_config=merged,
        auto_save=True
    )

    print(f"Final database host: {final_config.database.host}")


def configuration_inspection():
    """Inspecting and analyzing configuration."""
    config = ConfigManager('complex_config.yaml')

    # Flatten config for analysis
    flat_config = flatten_dict(config.raw_config)

    print("All configuration keys:")
    for key, value in flat_config.items():
        print(f"  {key}: {value}")

    # Check if config has been modified
    print(f"Config modified: {config.is_modified}")

    # Get all top-level sections
    print("Top-level sections:")
    for key in config.keys():
        print(f"  {key}")


def dynamic_configuration():
    """Dynamic configuration management."""
    config = ConfigManager('dynamic_config.yaml', auto_save=True)

    # Add configuration based on conditions
    if config.get('environment') == 'production':
        config.logging.level = 'WARNING'
        config.features.debug_toolbar = False
    else:
        config.logging.level = 'DEBUG'
        config.features.debug_toolbar = True

    # Dynamic feature flags
    feature_flags = {
        'new_ui': True,
        'beta_api': False,
        'experimental_cache': True
    }

    config.features.update(feature_flags)

    # Conditional service configuration
    if config.features.experimental_cache:
        config.cache = {
            'enabled': True,
            'backend': 'redis',
            'ttl': 3600
        }


def backup_and_restore():
    """Configuration backup and restore."""
    config = ConfigManager('important_config.yaml', backup=True)

    # Make changes
    original_host = config.database.host
    config.database.host = 'new-host.com'

    # Save with backup
    config.save()

    # Restore from backup if needed
    if something_went_wrong():
        config.reload()  # Or manually restore from .backup file
        print(f"Restored host: {config.database.host}")


def something_went_wrong():
    """Simulate an error condition."""
    return False


if __name__ == '__main__':
    microservices_example()
    environment_specific_configs()
    configuration_inspection()
    dynamic_configuration()
    backup_and_restore()
