from pydantic_settings import BaseSettings , SettingsConfigDict
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent.parent
ENV_FILE_PATH = APP_DIR / ".env"


class Settings(BaseSettings):
    app_name : str 
    app_version : str
    environment: str
    database_url : str
    jwt_secret_key: str
    jwt_algorithm: str
    jwt_access_token_expire_minutes: int
    redis_url : str
    ollama_host: str = "http://localhost:11434"
    embedding_model: str = "nomic-embed-text"
    llm_model : str = "gemma3:1b"
    rag_max_distance : float = 0.40
    rag_max_context_chars:int = 12000
    rag_max_anchors_per_note : int = 2
    rag_hybrid_top_k : int = 5

    
    model_config = SettingsConfigDict(env_file=ENV_FILE_PATH , env_file_encoding="utf-8" , case_sensitive=False)



settings = Settings()