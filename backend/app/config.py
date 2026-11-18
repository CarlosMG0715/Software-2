from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/evaluacion"
    secret_key: str = "cambia-esta-clave-larga"
    hash_salt: str = "cambia-esta-sal-larga"
    dominio_institucional: str = "universidad.edu.co"
    cors_origins: str = "http://localhost:5173"
    access_token_minutes: int = 60
    token_temporal_minutes: int = 30
    max_intentos: int = 5
    minutos_bloqueo: int = 15
    mostrar_token_en_respuesta: bool = True  # solo desarrollo: simula el envío de correo


settings = Settings()