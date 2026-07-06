from pydantic_settings import BaseSettings, SettingsConfigDict


__all__ = ("settings",)


class Settings(BaseSettings):
    database_url: str
    debug: bool

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


settings = Settings()
