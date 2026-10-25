import os

from dotenv import load_dotenv

load_dotenv()


APP_VERSION = "1.0.0"


class Settings:
    groq_api_key: str = os.getenv("GROQ_API_KEY", "")
    demo_mode: bool = os.getenv("DEMO_MODE", "false").lower() in {"1", "true", "yes", "on"}
    statsbomb_data_dir: str = os.getenv("STATSBOMB_DATA_DIR", "data")
    cors_origins: list[str] = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")


settings = Settings()
