from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    
    # How far ahead the dashboard projects expected income and commitments.
    FORECAST_HORIZON_DAYS: int = 30


    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )

settings = Settings()