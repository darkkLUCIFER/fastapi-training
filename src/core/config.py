from pydantic_settings import BaseSettings, SettingsConfigDict


__all__ = ('settings',)


class Settings(BaseSettings):
    database_url: str
    debug: bool
    cors_origins: list[str] = ['http://localhost:3000']

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
    )


settings = Settings()
