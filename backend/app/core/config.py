from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central app configuration, overridable via environment variables or a .env file."""

    app_name: str = "GamerZone API"
    app_version: str = "0.1.0"
    debug: bool = True
    database_url: str

    # No default for secret_key on purpose: the app must refuse to start rather than
    # fall back to a predictable value that would let anyone forge tokens.
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
