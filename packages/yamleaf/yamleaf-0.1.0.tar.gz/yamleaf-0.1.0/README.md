# Yamleaf

A Python package for managing YAML configuration files while preserving structure, comments, and formatting. Supports both dictionary and attribute access patterns with optional type validation.

## Features

- 🎯 **Preserves YAML Structure**: Comments, formatting, and key order maintained
- 🔧 **Multiple Access Patterns**: Dictionary, attribute, and dot notation access
- 🛡️ **Type Safety**: Optional type validation with dataclass integration
- 📁 **Auto-save**: Automatic saving on application exit
- 🔄 **Backup Support**: Automatic backup creation before saves
- 🏗️ **Create Missing Files**: Optionally create config files with defaults
- 🔍 **IDE Support**: Full autocomplete and type hints
- 📋 **List Support**: Native support for list operations
- 🎨 **Preserves Comments**: Your YAML comments stay intact

## Installation

```bash
pip install yamleaf
```

## Quick Start

### Basic Usage

```python
from yamleaf import ConfigManager

# Load existing config with auto-save
config = ConfigManager('config.yaml', auto_save=True)

# Dictionary-style access (familiar)
db_host = config['database.host']
config['database.port'] = 5432

# Attribute-style access (modern)
api_key = config.api.key
config.api.timeout = 30

# Mixed access patterns
config.logging.level = 'DEBUG'
config['features.new_ui'] = True
```

### With Type Validation

```python
from dataclasses import dataclass
from yamleaf import ConfigManager

@dataclass
class DatabaseConfig:
    host: str
    port: int
    ssl: bool

@dataclass
class AppConfig:
    name: str
    debug: bool
    database: DatabaseConfig

# Type-validated configuration
config = ConfigManager(
    'config.yaml',
    config_class=AppConfig,
    validate_types=True
)

# Automatic type conversion
config.database.port = "5432"  # Converted to int
config.debug = "false"         # Converted to bool
```

## Access Patterns

The package supports multiple ways to access your configuration:

### 1. Dictionary Access

```python
# Get values
host = config['database']['host']
port = config['database.port']  # Dot notation

# Set values
config['database']['host'] = 'new-host'
config['api.timeout'] = 60
```

### 2. Attribute Access

```python
# Get values
host = config.database.host
timeout = config.api.timeout

# Set values
config.database.host = 'new-host'
config.api.timeout = 60
```

### 3. Method Access

```python
# Get with defaults
host = config.get('database.host', 'localhost')

# Set values
config.set('database.host', 'new-host')

# Bulk updates
config.update({
    'database.host': 'new-host',
    'api.timeout': 60
})
```

## Working with Lists

```python
# Access list items
first_service = config.services[0]
service_name = config.services[0].name

# Modify lists
config.services[0].port = 8080
config.services.append({
    'name': 'new_service',
    'port': 9000
})
```

## Advanced Features

### Creating Missing Configs

```python
default_config = {
    'app': {'name': 'MyApp', 'version': '1.0.0'},
    'database': {'host': 'localhost', 'port': 5432}
}

config = ConfigManager(
    'new_config.yaml',
    create_if_missing=True,
    default_config=default_config
)
```

### Backup and Context Manager

```python
# With automatic backups
config = ConfigManager('config.yaml', backup=True)

# Context manager (auto-saves on exit)
with ConfigManager('config.yaml') as config:
    config.database.host = 'new-host'
    # Automatically saved when exiting context
```

### Type Validation

```python
@dataclass
class MyConfig:
    name: str
    port: int
    debug: bool

config = ConfigManager(
    'config.yaml',
    config_class=MyConfig,
    validate_types=True
)

# Type errors are caught and converted when possible
config.port = "8080"  # Automatically converted to int
```

## Migration from PyYAML

The package is designed as a drop-in replacement for PyYAML workflows:

### Before (PyYAML)

```python
import yaml

with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

db_host = config['database']['host']
config['database']['port'] = 5432

with open('config.yaml', 'w') as f:
    yaml.dump(config, f)  # Loses formatting!
```

### After (yamleaf)

```python
from yamleaf import ConfigManager

config = ConfigManager('config.yaml', auto_save=True)

# All your existing code still works
db_host = config['database']['host']
config['database']['port'] = 5432

# Plus new capabilities
db_host = config.database.host  # Attribute access
config.database.port = 5432    # Attribute setting

# Formatting preserved automatically!
```

## Configuration Examples

### Simple Web App

```yaml
app:
  name: "MyWebApp"
  port: 8080
  debug: false

database:
  host: "localhost"
  port: 5432
  name: "myapp"

api:
  timeout: 30
  rate_limit: 100
```

### Microservices

```yaml
services:
  - name: "auth_service"
    port: 8001
    endpoints: ["/login", "/logout"]

  - name: "api_service"
    port: 8002
    endpoints: ["/api/v1", "/api/v2"]

monitoring:
  enabled: true
  metrics_port: 9090
```

## Real-World Examples

### Backend Integration Service

```python
from yamleaf import ConfigManager

# Perfect for your Python backend integrations
config = ConfigManager('integration_config.yaml', auto_save=True)

# API configurations for different services
config.services.stripe.api_key = "sk_live_..."
config.services.stripe.webhook_secret = "whsec_..."
config.services.sendgrid.api_key = "SG...."

# Database connections
config.databases.primary.host = "prod-db.company.com"
config.databases.analytics.host = "analytics-db.company.com"

# AI agent configurations
config.ai_agents.chatbot.model = "gpt-4"
config.ai_agents.chatbot.temperature = 0.7
config.ai_agents.classifier.confidence_threshold = 0.85

# Bot configurations
config.bots.slack_bot.token = "xoxb-..."
config.bots.discord_bot.enabled = True
config.bots.telegram_bot.polling_interval = 30
```

### Automated Bot Configuration

```python
# Load bot configuration with type validation
@dataclass
class BotConfig:
    name: str
    token: str
    channels: list
    enabled: bool
    rate_limit: int

config = ConfigManager(
    'bot_config.yaml',
    config_class=BotConfig,
    validate_types=True
)

# Easy bot management
for bot_name in config.bots.keys():
    bot = config.bots[bot_name]
    if bot.enabled:
        print(f"Starting {bot.name} bot on {len(bot.channels)} channels")

# Runtime configuration updates
config.bots.monitoring_bot.rate_limit = 100
config.bots.news_bot.channels.append("#tech-news")
```

## API Reference

### ConfigManager

#### Constructor

```python
ConfigManager(
    config_path: Union[str, Path],
    config_class: Optional[type] = None,
    auto_save: bool = True,
    backup: bool = False,
    indent: int = 2,
    sequence_indent: int = 4,
    validate_types: bool = True,
    create_if_missing: bool = False,
    default_config: Optional[Dict[str, Any]] = None
)
```

**Parameters:**
- `config_path`: Path to the YAML configuration file
- `config_class`: Optional dataclass for type validation
- `auto_save`: Automatically save changes on exit
- `backup`: Create backup before saving
- `indent`: YAML indentation for maps
- `sequence_indent`: YAML indentation for sequences
- `validate_types`: Enable type validation
- `create_if_missing`: Create config file if it doesn't exist
- `default_config`: Default configuration for new files

#### Methods

- `get(key_path: str, default: Any = None) -> Any`: Get value using dot notation
- `set(key_path: str, value: Any) -> None`: Set value using dot notation
- `update(updates: Dict[str, Any]) -> None`: Update multiple values
- `delete(key_path: str) -> None`: Delete a configuration key
- `save(path: Optional[Union[str, Path]] = None) -> None`: Save configuration
- `reload() -> None`: Reload from file, discarding changes
- `reset() -> None`: Reset to default configuration

#### Properties

- `config: ConfigProxy`: Attribute access proxy
- `is_modified: bool`: Check if configuration has been modified
- `raw_config: Dict[str, Any]`: Raw configuration dictionary

### ConfigProxy

The `ConfigProxy` class provides attribute-style access to configuration values:

```python
# Access nested values
config.database.host
config.api.endpoints[0]

# Set nested values
config.database.host = "new-host"
config.features.new_ui = True

# Convert back to dictionary
config.database.to_dict()
```

## Error Handling

The package provides specific exceptions for different error conditions:

```python
from yamleaf import (
    ConfigManager, 
    ConfigError, 
    ConfigNotFoundError, 
    ConfigValidationError
)

try:
    config = ConfigManager('config.yaml')
except ConfigNotFoundError:
    print("Config file not found, creating default...")
    config = ConfigManager(
        'config.yaml',
        create_if_missing=True,
        default_config={'app': {'name': 'MyApp'}}
    )
except ConfigValidationError as e:
    print(f"Config validation failed: {e}")
except ConfigError as e:
    print(f"Config error: {e}")
```

## Best Practices

### 1. Use Type Validation for Production

```python
@dataclass
class ProductionConfig:
    database_url: str
    api_key: str
    debug: bool = False

config = ConfigManager(
    'prod_config.yaml',
    config_class=ProductionConfig,
    validate_types=True,
    backup=True
)
```

### 2. Environment-Specific Configurations

```python
import os

env = os.getenv('ENVIRONMENT', 'development')
config = ConfigManager(f'config_{env}.yaml', auto_save=True)

# Environment-specific settings
if env == 'production':
    config.logging.level = 'WARNING'
else:
    config.logging.level = 'DEBUG'
```

### 3. Configuration Inheritance

```python
from yamleaf.utils import merge_configs

# Load base configuration
base = ConfigManager('base_config.yaml', auto_save=False)

# Load environment overrides
env_overrides = ConfigManager('production_overrides.yaml', auto_save=False)

# Merge configurations
merged_config = merge_configs(base.raw_config, env_overrides.raw_config)

# Create final configuration
config = ConfigManager(
    'final_config.yaml',
    create_if_missing=True,
    default_config=merged_config
)
```

### 4. Configuration Validation

```python
from yamleaf.utils import validate_config_structure

# Define required structure
required_schema = {
    'database': dict,
    'api': dict,
    'logging': dict
}

config = ConfigManager('config.yaml')
errors = validate_config_structure(config.raw_config, required_schema)

if errors:
    print("Configuration errors found:")
    for error in errors:
        print(f"  - {error}")
```

## Integration Examples

### Flask Application

```python
from flask import Flask
from yamleaf import ConfigManager

app = Flask(__name__)

# Load configuration
config = ConfigManager('flask_config.yaml', auto_save=True)

# Configure Flask
app.config['SECRET_KEY'] = config.flask.secret_key
app.config['SQLALCHEMY_DATABASE_URI'] = config.database.url

# Runtime configuration updates
@app.route('/admin/config')
def update_config():
    config.features.maintenance_mode = True
    return "Maintenance mode enabled"
```

### FastAPI Application

```python
from fastapi import FastAPI
from yamleaf import ConfigManager

config = ConfigManager('fastapi_config.yaml')
app = FastAPI(
    title=config.api.title,
    version=config.api.version,
    debug=config.app.debug
)

@app.on_event("startup")
async def startup_event():
    # Initialize services based on config
    if config.services.redis.enabled:
        # Initialize Redis connection
        pass
```

### Celery Worker

```python
from celery import Celery
from yamleaf import ConfigManager

config = ConfigManager('celery_config.yaml')

app = Celery(
    config.celery.name,
    broker=config.celery.broker_url,
    backend=config.celery.result_backend
)

# Dynamic task routing
app.conf.task_routes = config.celery.task_routes.to_dict()
```

## Performance Considerations

The package is designed for configuration management, not high-frequency data access. For best performance:

1. **Load once**: Create the ConfigManager instance once and reuse it
2. **Cache frequently accessed values**: Store commonly used config values in variables
3. **Use raw_config for bulk operations**: For large-scale config processing, use `config.raw_config`

```python
# Good: Load once, reuse
config = ConfigManager('config.yaml')
db_host = config.database.host  # Cache if used frequently

# Avoid: Loading repeatedly
# config = ConfigManager('config.yaml')  # Don't do this in loops
```

## Troubleshooting

### Common Issues

1. **AttributeError on missing keys**:
```python
# Use get() with defaults for optional keys
timeout = config.get('api.timeout', 30)

# Or check existence first
if hasattr(config.api, 'timeout'):
    timeout = config.api.timeout
```

2. **Type validation errors**:
```python
# Ensure your YAML types match dataclass expectations
# Or disable validation for flexible configs
config = ConfigManager('config.yaml', validate_types=False)
```

3. **File permission errors**:
```python
# Ensure write permissions for auto-save
config = ConfigManager('config.yaml', auto_save=False)
# Manually save when needed
config.save()
```

## Requirements

- Python 3.8+
- ruamel.yaml >= 0.17.0

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Development Setup

```bash
git clone https://github.com/yourusername/yamleaf.git
cd yamleaf
pip install -e ".[dev]"
pytest
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=yamleaf

# Run specific test
pytest tests/test_config_manager.py::TestConfigManager::test_attribute_access
```

## Changelog

### Version 0.1.0

- Initial release
- Dictionary and attribute access patterns
- Type validation with dataclass integration
- Auto-save functionality
- Backup support
- List operations support
- YAML structure preservation
- Comprehensive test suite

## Author

Created by Aaron Z. (mildthrone@proton.me) 
