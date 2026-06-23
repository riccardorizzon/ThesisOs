from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    app_env: str = "local"
    log_level: str = "INFO"
    database_url: str = "postgresql+psycopg://thesisos:thesisos@localhost:5432/thesisos"
    google_cloud_project: str = ""
    vertex_location: str = "europe-west1"
    gemini_model: str = "gemini-2.5-pro"
    embedding_model: str = "text-multilingual-embedding-002"


settings = Settings()
