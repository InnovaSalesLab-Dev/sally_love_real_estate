"""
Application configuration and settings
Loads environment variables and provides centralized configuration
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Environment
    ENVIRONMENT: str = "development"
    
    # Server Configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WEBHOOK_BASE_URL: str = "http://localhost:8000"
    
    # Vapi Configuration
    VAPI_API_KEY: str = ""
    VAPI_PHONE_NUMBER_ID: Optional[str] = None
    VAPI_API_URL: str = "https://api.vapi.ai"
    
    # BoldTrail CRM Configuration
    BOLDTRAIL_API_KEY: str = ""
    BOLDTRAIL_API_URL: str = "https://api.kvcore.com/v2/public"
    BOLDTRAIL_ACCOUNT_ID: str = ""
    BOLDTRAIL_ZAPIER_KEY: str = ""
    
    # Stellar MLS Configuration
    STELLAR_MLS_USERNAME: str = ""
    STELLAR_MLS_PASSWORD: str = ""
    STELLAR_MLS_API_URL: str = "https://api.stellarmls.com/v1"
    
    # Twilio Configuration
    TWILIO_ACCOUNT_SID: str = ""
    TWILIO_AUTH_TOKEN: str = ""
    TWILIO_PHONE_NUMBER: str = "+13523992010"
    
    # Business Configuration
    BUSINESS_NAME: str = "Sally Love Real Estate"
    BUSINESS_PHONE: str = "+13523992010"
    OFFICE_HOURS_START: str = "09:00"
    OFFICE_HOURS_END: str = "17:00"
    OFFICE_TIMEZONE: str = "America/New_York"
    
    # Testing Configuration
    TEST_MODE: bool = True
    TEST_AGENT_NAME: str = "Hammas Ali"
    TEST_AGENT_PHONE: str = "+923035699010"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/app.log"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment"""
        return self.ENVIRONMENT.lower() == "production"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development environment"""
        return self.ENVIRONMENT.lower() == "development"


# Create global settings instance
settings = Settings()

