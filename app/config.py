from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    llm_provider: str = "gemini"
    gemini_api_key: str = ""
    openai_api_key: str = ""
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    notify_email: str = ""
    admin_password: str = "admin123"
    api_base_url: str = "http://localhost:8000"

    data_dir: Path = Path("data")
    db_path: Path = Path("data/leads.db")

    @property
    def email_enabled(self) -> bool:
        return bool(self.smtp_user and self.smtp_password and self.notify_email)


settings = Settings()
