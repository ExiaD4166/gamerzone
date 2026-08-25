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

    redis_url: str

    mail_host: str
    mail_port: int = 1025
    mail_username: str = ""
    mail_password: str = ""
    mail_use_tls: bool = False
    mail_from: str = "noreply@gamerzone.local"
    mail_from_name: str = "GamerZone"

    email_verification_expire_hours: int = 24
    verification_url_base: str

    # Much shorter than verification: a leaked reset link hands over the whole account,
    # so the window in which one is useful is kept small.
    password_reset_expire_minutes: int = 60
    password_reset_url_base: str

    # Browsers refuse cross-origin calls unless the server names the caller, so the
    # frontend's address has to be listed here. Comma-separated; never "*", because a
    # wildcard is incompatible with allow_credentials and would let any site call this
    # API with the user's token.
    cors_origins: str = "http://localhost:3000"
    log_level: str = "INFO"

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
