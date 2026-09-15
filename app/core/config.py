from pydantic_settings import BaseSettings , SettingsConfigDict
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent.parent
ENV_FILE_PATH = APP_DIR / ".env"


class Settings(BaseSettings):
    app_name : str 
    app_version : str
    environment: str
    database_url : str

    model_config = SettingsConfigDict(env_file=ENV_FILE_PATH , env_file_encoding="utf-8" , case_sensitive=False)



settings = Settings()