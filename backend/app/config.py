from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/evaluacion"
    secret_key: str = "cambia-esta-clave-larga"
    hash_salt: str = "cambia-esta-sal-larga"
    dominio_institucional: str = "universidad.edu.co"
    cors_origins: str = "http://localhost:5173"
    access_token_minutes: int = 60
    max_intentos: int = 5
    minutos_bloqueo: int = 15

    @field_validator("database_url")
    @classmethod
    def _normalizar_url(cls, v: str) -> str:
        # Render entrega postgres:// o postgresql://; SQLAlchemy necesita el driver explícito.
        if v.startswith("postgres://"):
            v = "postgresql://" + v[len("postgres://"):]
        if v.startswith("postgresql://"):
            v = "postgresql+psycopg2://" + v[len("postgresql://"):]
        return v


settings = Settings()
