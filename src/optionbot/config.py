"""Central config: env vars + .env file. No secrets in code."""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    ENV: str = "development"
    PORT: int = 8000

    MAX_DAILY_LOSS: float = 5000.0
    MAX_POSITION_QTY: int = 200
    KILL_SWITCH: bool = False

    KITE_API_KEY: str = ""
    KITE_API_SECRET: str = ""
    KITE_ACCESS_TOKEN: str = ""

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
