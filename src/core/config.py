from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


__all__ = ('settings',)


class Settings(BaseSettings):
    database_url: str
    debug: bool
    cors_origins: list[str] = ['http://localhost:3000']

    @field_validator('database_url')
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        """Ensure database URL uses PostgreSQL syntax if needed."""
        if v.startswith('sqlite:///'):
            # Optionally warn about using SQLite in production
            print('Warning: Using SQLite!!! For production, use PostgreSQL.')  # noqa
        return v

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
    )


settings = Settings()
