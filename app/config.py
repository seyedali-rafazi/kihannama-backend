import os
import re
from pathlib import Path
from typing import List, Union
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

    DATABASE_URL: str = ""
    DATABASE_URL_UNPOOLED: str = ""
    
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "kihannama"

    PORT: int = 8000
    HOST: str = "0.0.0.0"
    CORS_ORIGINS: Union[List[str], str] = ["http://localhost:5173", "http://127.0.0.1:5173", "https://kihannama.ir"]

    ACTIVE_SATELLITE_PATH: str = "data/active-satellite.txt"
    STATION_OPS_PATH: str = "data/station-ops.csv"

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v):
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        return ["*"]

    @property
    def RESOLVED_ACTIVE_SATELLITE_PATH(self) -> Path:
        p = Path(self.ACTIVE_SATELLITE_PATH)
        if not p.is_absolute():
            cand1 = (BASE_DIR / p).resolve()
            if cand1.exists():
                return cand1
            cand2 = (BASE_DIR.parent / p).resolve()
            if cand2.exists():
                return cand2
            cand3 = (BASE_DIR.parent / "src" / "data" / "active-satellite.txt").resolve()
            if cand3.exists():
                return cand3
        return p.resolve()

    @property
    def RESOLVED_STATION_OPS_PATH(self) -> Path:
        p = Path(self.STATION_OPS_PATH)
        if not p.is_absolute():
            cand1 = (BASE_DIR / p).resolve()
            if cand1.exists():
                return cand1
            cand2 = (BASE_DIR.parent / p).resolve()
            if cand2.exists():
                return cand2
            cand3 = (BASE_DIR.parent / "src" / "data" / "station-ops.csv").resolve()
            if cand3.exists():
                return cand3
        return p.resolve()

    @property
    def ASYNC_DATABASE_URL(self) -> str:
        url = self.DATABASE_URL
        if url.startswith("postgresql://"):
            url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
        elif url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql+asyncpg://", 1)
        
        # Format query parameters for asyncpg
        url = url.replace("sslmode=require", "ssl=require")
        # Remove channel_binding if present since asyncpg doesn't support it directly in query string
        url = re.sub(r"[?&]channel_binding=[^&]+", "", url)
        if "?" not in url and "&" in url:
            url = url.replace("&", "?", 1)
        return url

settings = Settings()
