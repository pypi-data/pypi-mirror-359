"""Base settings for AI Agent Studio."""

from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class AIServiceKeySettings(BaseSettings):
    """Settings for AIServiceKey."""

    model_config: SettingsConfigDict = SettingsConfigDict(
        env_file=".env", extra="allow"
    )
    openai_api_key: str | None = None
    anthropic_api_key: str | None = None


ai_service_key_settings = AIServiceKeySettings()


class ApplicationSettings(BaseSettings):
    """Settings for App."""

    model_config: SettingsConfigDict = SettingsConfigDict(
        env_prefix="APP_", env_file=".env", extra="allow"
    )
    name: str = "axmp-ai-agent-studio"
    title: str = "AXMP AI Agent Studio"
    version: str | None = None
    description: str = "AXMP AI Agent Studio Backend Service Restful API"
    root_path: str = "/api/ai/studio/v1"
    docs_url: str = f"{root_path}/api-docs"
    redoc_url: str = f"{root_path}/api-redoc"
    openapi_url: str = f"{root_path}/openapi"


application_settings = ApplicationSettings()


class StudioSettings(BaseSettings):
    """Settings for AI."""

    model_config: SettingsConfigDict = SettingsConfigDict(
        env_prefix="STUDIO_", env_file=".env", extra="allow"
    )

    api_endpoint: str
    default_model: str = "openai/gpt-4.1-mini"
    default_model_max_tokens: int = 5000
    recursion_limit: int = 30
    stream_mode: Literal["messages", "values", "updates"] = "messages"
    temperature: float = 0


studio_settings = StudioSettings()


class LoggerSettings(BaseSettings):
    """Settings for Logger."""

    model_config: SettingsConfigDict = SettingsConfigDict(
        env_prefix="LOG_", env_file=".env", extra="allow"
    )
    config_file: str = "logging.conf"
    level: str = "INFO"


logger_settings = LoggerSettings()


class MongoDBSettings(BaseSettings):
    """Settings for MongoDB."""

    model_config: SettingsConfigDict = SettingsConfigDict(
        env_prefix="MONGODB_", env_file=".env", extra="allow"
    )

    hostname: str
    port: int
    username: str
    password: str
    database: str
    connection_timeout_ms: int = 5000

    # Collection names
    collection_llm_model: str = "llm_model"
    collection_kubernetes_profile: str = "kubernetes_profile"
    collection_backend_server: str = "backend_server"
    collection_mcp_profile: str = "mcp_profile"
    collection_agent_profile: str = "agent_profile"

    @property
    def uri(self) -> str:
        """Get MongoDB connection URI."""
        return f"mongodb://{self.username}:{self.password}@{self.hostname}:{self.port}/{self.database}"


mongodb_settings = MongoDBSettings()


# class PostgreSQLSettings(BaseSettings):
#     """Settings for PostgreSQL."""

#     model_config: SettingsConfigDict = SettingsConfigDict(
#         env_prefix="POSTGRESQL_", env_file=".env", extra="allow"
#     )

#     hostname: str
#     port: int
#     username: str
#     password: str
#     database: str
#     # Connection timeout settings
#     connect_timeout: int = 10
#     # TCP keepalive settings
#     tcp_keepalives_idle: int = 600  # 10 minutes
#     tcp_keepalives_interval: int = 30  # 30 seconds
#     tcp_keepalives_count: int = 3
#     # SSL settings
#     sslmode: str = "prefer"
#     # Application name for connection identification
#     application_name: str = "zmp_aiops_pilot"

#     @property
#     def db_uri(self) -> str:
#         """Return the connection string for the PostgreSQL database."""
#         return f"postgresql://{self.username}:{self.password}@{self.hostname}:{self.port}/{self.database}"

#     @property
#     def db_uri_with_params(self) -> str:
#         """Return the connection string with additional parameters for connection stability."""
#         params = [
#             f"connect_timeout={self.connect_timeout}",
#             f"sslmode={self.sslmode}",
#             f"application_name={self.application_name}",
#             f"keepalives_idle={self.tcp_keepalives_idle}",
#             f"keepalives_interval={self.tcp_keepalives_interval}",
#             f"keepalives_count={self.tcp_keepalives_count}",
#         ]

#         param_string = "&".join(params)
#         return f"{self.db_uri}?{param_string}"


# postgresql_settings = PostgreSQLSettings()
