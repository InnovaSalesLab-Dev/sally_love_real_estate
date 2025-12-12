"""
Validation utilities for input data
"""

import re
import phonenumbers
from datetime import datetime
from typing import Optional
from .errors import ValidationError


def validate_phone(phone: str) -> str:
    """
    Validate and format phone number
    
    Args:
        phone: Phone number string
        
    Returns:
        Formatted phone number in E.164 format
        
    Raises:
        ValidationError: If phone number is invalid
    """
    try:
        parsed = phonenumbers.parse(phone, "US")
        if not phonenumbers.is_valid_number(parsed):
            raise ValidationError(
                message="Invalid phone number",
                field="phone",
                details={"phone": phone}
            )
        return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
    except phonenumbers.NumberParseException as e:
        raise ValidationError(
            message=f"Invalid phone number format: {str(e)}",
            field="phone",
            details={"phone": phone}
        )


def validate_email(email: str) -> str:
    """
    Validate email address format
    
    Args:
        email: Email address string
        
    Returns:
        Lowercase email address
        
    Raises:
        ValidationError: If email is invalid
    """
    email = email.lower().strip()
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not re.match(pattern, email):
        raise ValidationError(
            message="Invalid email address format",
            field="email",
            details={"email": email}
        )
    
    return email


def validate_date(date_str: str, format: str = "%Y-%m-%d") -> datetime:
    """
    Validate and parse date string
    
    Args:
        date_str: Date string to validate
        format: Expected date format (default: YYYY-MM-DD)
        
    Returns:
        Parsed datetime object
        
    Raises:
        ValidationError: If date format is invalid
    """
    try:
        return datetime.strptime(date_str, format)
    except ValueError as e:
        raise ValidationError(
            message=f"Invalid date format. Expected {format}",
            field="date",
            details={"date": date_str, "error": str(e)}
        )


def validate_required_fields(data: dict, required_fields: list) -> None:
    """
    Validate that all required fields are present in data
    
    Args:
        data: Dictionary to validate
        required_fields: List of required field names
        
    Raises:
        ValidationError: If any required field is missing
    """
    missing_fields = [field for field in required_fields if field not in data or not data[field]]
    
    if missing_fields:
        raise ValidationError(
            message=f"Missing required fields: {', '.join(missing_fields)}",
            details={"missing_fields": missing_fields}
        )

