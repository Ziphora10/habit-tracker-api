import os


class Settings:
    """Application settings, sourced from environment variables with sane defaults."""

    PROJECT_NAME: str = "Habit Tracker API"
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./habit_tracker.db")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key-change-me-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))


settings = Settings()
