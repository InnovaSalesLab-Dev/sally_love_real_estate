"""
Application configuration and settings
Loads environment variables and provides centralized configuration
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables
    
    All values are loaded from .env file or environment variables.
    No hardcoded defaults for configuration values.
    """
    
    # Environment
    ENVIRONMENT: str  # Must be set in .env
    
    # Server Configuration
    HOST: str  # Must be set in .env
    PORT: int  # Must be set in .env
    WEBHOOK_BASE_URL: str  # Must be set in .env
    
    # Vapi Configuration
    VAPI_API_KEY: str  # Must be set in .env
    VAPI_PHONE_NUMBER_ID: Optional[str] = None  # Optional
    VAPI_API_URL: str = "https://api.vapi.ai"  # Static - never changes
    VAPI_ASSISTANT_ID: str = ""  # Required if using GHL webhooks - your Vapi assistant ID

    # CORS - Optional, comma-separated origins for production (e.g. "https://app.example.com")
    CORS_ORIGINS: str = ""

    # BoldTrail CRM Configuration
    BOLDTRAIL_API_KEY: str  # Must be set in .env
    BOLDTRAIL_API_URL: str = "https://api.kvcore.com/v2/public"  # Static - never changes
    BOLDTRAIL_ACCOUNT_ID: str  # Must be set in .env
    BOLDTRAIL_ZAPIER_KEY: str  # Must be set in .env
    
    # Stellar MLS Configuration (Optional - not currently used)
    STELLAR_MLS_USERNAME: str = ""
    STELLAR_MLS_PASSWORD: str = ""
    STELLAR_MLS_API_URL: str = "https://api.stellarmls.com/v1"  # Static
    
    # Twilio Configuration
    TWILIO_ACCOUNT_SID: str  # Must be set in .env
    TWILIO_AUTH_TOKEN: str  # Must be set in .env
    TWILIO_PHONE_NUMBER: str  # Must be set in .env
    
    # Business Configuration
    BUSINESS_NAME: str  # Must be set in .env
    BUSINESS_PHONE: str  # Must be set in .env
    OFFICE_HOURS_START: str  # Must be set in .env
    OFFICE_HOURS_END: str  # Must be set in .env
    OFFICE_TIMEZONE: str  # Must be set in .env
    
    # Lead Notification Configuration (who gets notified when leads are created)
    OFFICE_NOTIFICATION_PHONE: str  # Must be set in .env
    OFFICE_NOTIFICATION_EMAIL: str = ""  # Optional - office/Jeff email for dual SMS+email alerts
    JEFF_NOTIFICATION_PHONE: str = ""  # Optional - empty if not set
    JEFF_NOTIFICATION_EMAIL: str = ""  # Optional - if empty, use OFFICE_NOTIFICATION_EMAIL for Jeff
    LEAD_NOTIFICATION_ENABLED: bool  # Must be set in .env

    # Agent Roster (source of truth for transfers, replaces BoldTrail for agent lookup)
    AGENT_ROSTER_PATH: str = "data/agent_roster.json"  # Path relative to project root
    
    # Testing Configuration
    TEST_MODE: bool  # Must be set in .env
    TEST_AGENT_NAME: str  # Must be set in .env
    TEST_AGENT_PHONE: str  # Must be set in .env

    # Logging
    LOG_LEVEL: str  # Must be set in .env
    LOG_FILE: str  # Must be set in .env

    # Email (SMTP) - Optional, for email notifications
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_FROM_EMAIL: str = ""
    SMTP_USERNAME: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_USE_TLS: bool = True

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

