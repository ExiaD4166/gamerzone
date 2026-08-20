from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central app configuration, overridable via environment variables or a .env file."""

    app_name: str = "GamerZone API"
    app_version: str = "0.1.0"
    debug: bool = True
    database_url: str

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
