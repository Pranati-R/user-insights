from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "UserInsight AI"
    mongo_uri: str = "mongodb://localhost:27017"
    mongo_db: str = "userinsight"
    events_collection: str = "events"
    sessions_collection: str = "sessions"
    anomalies_collection: str = "anomalies"
    users_collection: str = "users"
    websites_collection: str = "websites"

    hf_model_repo: str = "sklearn-docs/anomaly-detection"
    hf_model_filename: str = "isolation_forest.pkl"
    hf_token: str | None = None

    anomaly_score_threshold: float = 0.5
    session_idle_minutes: int = 30

    jwt_secret: str = "super-secret-key"
    jwt_algorithm: str = "HS256"
    jwt_exp_minutes: int = 60

    tracking_base_url: str = "http://localhost:8000"
    cors_origins: list[str] = ["https://vcode7.github.io","http://localhost:5173","http://localhost:5174","http://localhost:5175"]
    
    # Groq API for intelligent log parsing (optional)
    groq_api_key: str | None = None

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="allow")


@lru_cache
def get_settings() -> Settings:
    return Settings()


