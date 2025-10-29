from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import AnyUrl, AnyHttpUrl

class Settings(BaseSettings):
    BOT_TOKEN: str
    DB_URL: AnyUrl | str

    ADMIN_PANEL_URL: AnyHttpUrl
    ADMIN_JWT_SECRET: str
    ADMIN_JWT_EXPIRES_MIN: int = 120

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore",
    )

settings = Settings()
