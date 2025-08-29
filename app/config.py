from pydantic import BaseModel
import os
from dotenv import load_dotenv


class Settings(BaseModel):
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./app.db")


    OPENAI_API_KEY: str | None = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")


    SLACK_WEBHOOK_URL: str | None = os.getenv("SLACK_WEBHOOK_URL")
    EMAIL_FROM: str = os.getenv("EMAIL_FROM", "noreply@example.com")
    SMTP_HOST: str | None = os.getenv("SMTP_HOST")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USERNAME: str | None = os.getenv("SMTP_USERNAME")
    SMTP_PASSWORD: str | None = os.getenv("SMTP_PASSWORD")


    API_KEY: str | None = os.getenv("API_KEY")


settings = Settings()
