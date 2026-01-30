"""
Custom exception classes for the application
"""

from typing import Optional, Dict, Any


class VapiError(Exception):
    """Base exception for Vapi-related errors"""
    
    def __init__(
        self,
        message: str,
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class IntegrationError(Exception):
    """Exception for external integration errors (CRM, MLS, Twilio, etc.)"""
    
    def __init__(
        self,
        message: str,
        service: str,
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.message = message
        self.service = service
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class ValidationError(Exception):
    """Exception for validation errors"""
    
    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.message = message
        self.field = field
        self.details = details or {}
        super().__init__(self.message)


class BoldTrailError(IntegrationError):
    """Exception for BoldTrail CRM errors"""
    
    def __init__(self, message: str, status_code: int = 500, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, service="BoldTrail CRM", status_code=status_code, details=details)


class StellarMLSError(IntegrationError):
    """Exception for Stellar MLS errors"""
    
    def __init__(self, message: str, status_code: int = 500, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, service="Stellar MLS", status_code=status_code, details=details)


class TwilioError(IntegrationError):
    """Exception for Twilio errors"""

    def __init__(self, message: str, status_code: int = 500, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, service="Twilio", status_code=status_code, details=details)


class EmailError(IntegrationError):
    """Exception for email (SMTP) errors"""

    def __init__(self, message: str, status_code: int = 500, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, service="SMTP", status_code=status_code, details=details)

