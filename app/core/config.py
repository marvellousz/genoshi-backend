import os
from pathlib import Path
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    app_name: str = "Insurance Document Validator API"
    app_version: str = "1.0.0"
    debug: bool = False
    
    host: str = "0.0.0.0"
    port: int = 8000
    
    groq_api_key: str = os.getenv("GROQ_API_KEY", "")
    ai_model: str = "llama-3.3-70b-versatile"
    ai_temperature: float = 0.1
    ai_max_tokens: int = 500
    
    log_level: str = "INFO"
    
    base_dir: Path = Path(__file__).parent.parent.parent
    data_dir: Path = base_dir / "data"
    valid_vessels_file: Path = data_dir / "valid_vessels.json"
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"


settings = Settings()
