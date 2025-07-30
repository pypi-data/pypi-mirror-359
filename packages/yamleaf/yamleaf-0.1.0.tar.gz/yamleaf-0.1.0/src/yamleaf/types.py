"""
Type definitions and example configuration classes.
"""

from typing import Protocol, runtime_checkable, Dict, List, Optional, Any
from dataclasses import dataclass, field


@runtime_checkable
class ConfigProtocol(Protocol):
    """Protocol for configuration classes."""
    pass


@dataclass
class DatabaseConfig:
    """Database configuration settings."""
    host: str = "localhost"
    port: int = 5432
    name: str = "myapp"
    username: str = "user"
    password: str = "password"
    ssl: bool = False
    timeout: int = 30
    pool_size: int = 10
    max_connections: int = 20
    connection_params: Dict[str, Any] = field(default_factory=dict)


@dataclass
class APIConfig:
    """API configuration settings."""
    base_url: str = "https://api.example.com"
    timeout: int = 30
    retries: int = 3
    rate_limit: int = 100
    key: str = ""
    secret: str = ""
    version: str = "v1"
    headers: Dict[str, str] = field(default_factory=dict)
    endpoints: Dict[str, str] = field(default_factory=dict)


@dataclass
class LoggingConfig:
    """Logging configuration settings."""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file: str = "app.log"
    max_size: int = 10485760  # 10MB
    backup_count: int = 5
    console: bool = True
    json_format: bool = False
    handlers: List[str] = field(default_factory=lambda: ["console", "file"])


@dataclass
class CacheConfig:
    """Cache configuration settings."""
    enabled: bool = True
    backend: str = "memory"  # memory, redis, memcached
    ttl: int = 3600  # seconds
    max_size: int = 1000
    host: str = "localhost"
    port: int = 6379
    prefix: str = "app"
    options: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SecurityConfig:
    """Security configuration settings."""
    secret_key: str = "change-me-in-production"
    jwt_secret: str = "jwt-secret-key"
    jwt_expiry: int = 3600
    password_hash_rounds: int = 12
    max_login_attempts: int = 5
    session_timeout: int = 1800
    cors_origins: List[str] = field(default_factory=list)
    allowed_hosts: List[str] = field(default_factory=list)


@dataclass
class FeatureFlags:
    """Feature flag configuration."""
    new_ui: bool = False
    beta_features: bool = False
    experimental_api: bool = False
    debug_mode: bool = False
    maintenance_mode: bool = False
    analytics: bool = True


@dataclass
class MonitoringConfig:
    """Monitoring and metrics configuration."""
    enabled: bool = True
    metrics_port: int = 9090
    health_check_interval: int = 30
    alert_webhook: str = ""
    prometheus_enabled: bool = False
    jaeger_enabled: bool = False
    log_requests: bool = True


@dataclass
class AppConfig:
    """Complete application configuration."""
    app_name: str = "MyApp"
    version: str = "1.0.0"
    debug: bool = False
    environment: str = "development"  # development, staging, production

    # Sub-configurations
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    api: APIConfig = field(default_factory=APIConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    cache: CacheConfig = field(default_factory=CacheConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    features: FeatureFlags = field(default_factory=FeatureFlags)
    monitoring: MonitoringConfig = field(default_factory=MonitoringConfig)

    # Additional settings
    plugins: List[str] = field(default_factory=list)
    custom_settings: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ServiceConfig:
    """Microservice configuration."""
    name: str
    port: int
    host: str = "localhost"
    enabled: bool = True
    endpoints: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    resources: Dict[str, Any] = field(default_factory=dict)
    env_vars: Dict[str, str] = field(default_factory=dict)
    health_check: str = "/health"
    metrics_endpoint: str = "/metrics"


@dataclass
class WorkerConfig:
    """Worker/queue configuration."""
    enabled: bool = True
    workers: int = 4
    queue_backend: str = "redis"  # redis, rabbitmq, memory
    queue_host: str = "localhost"
    queue_port: int = 6379
    queue_db: int = 0
    max_retries: int = 3
    retry_delay: int = 60
    task_timeout: int = 300
    prefetch_count: int = 1


@dataclass
class EmailConfig:
    """Email configuration."""
    enabled: bool = False
    smtp_host: str = "localhost"
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    use_tls: bool = True
    from_email: str = "noreply@example.com"
    from_name: str = "MyApp"
    templates_dir: str = "templates/email"


@dataclass
class StorageConfig:
    """File storage configuration."""
    backend: str = "local"  # local, s3, gcs, azure
    base_path: str = "/var/data"
    bucket_name: str = ""
    region: str = "us-east-1"
    access_key: str = ""
    secret_key: str = ""
    cdn_url: str = ""
    max_file_size: int = 104857600  # 100MB
    allowed_extensions: List[str] = field(default_factory=lambda: [".jpg", ".png", ".pdf"])
