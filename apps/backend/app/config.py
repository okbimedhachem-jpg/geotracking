from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "GeoTracking"
    env: str = "development"

    secret_key: str = "dev-secret-key-change-me"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24

    postgres_db: str = "geotracking"
    postgres_user: str = "geotracking"
    postgres_password: str = "geotracking"
    postgres_host: str = "localhost"
    postgres_port: int = 5432

    api_host: str = "0.0.0.0"
    api_port: int = 8000

    class Config:
        env_file = ".env"


settings = Settings()
