from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    app_env: str = "local"
    log_level: str = "INFO"
    database_url: str = "postgresql+psycopg://thesisos:thesisos@localhost:5432/thesisos"
    google_cloud_project: str = ""
    vertex_location: str = "global"
    gemini_model: str = "gemini-3.6-flash"
    gemini_orchestration_model: str = "gemini-3.5-flash-lite"
    embedding_model: str = "text-multilingual-embedding-002"
    # M3 document storage (spec §4.1): "local" filesystem adapter or "gcs".
    document_storage_backend: str = "local"
    document_storage_local_dir: str = "/tmp/thesisos-documents"
    documents_bucket: str = ""


settings = Settings()
