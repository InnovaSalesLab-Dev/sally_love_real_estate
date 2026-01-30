"""
Tests for send_notification function and email/SMS delivery
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


# ---------------------------------------------------------------------------
# send_notification endpoint tests (mocked to avoid real SMS/email)
# ---------------------------------------------------------------------------


@patch("src.functions.send_notification.EmailClient")
@patch("src.functions.send_notification.TwilioClient")
def test_send_notification_sms_only(mock_twilio_cls, mock_email_cls):
    """SMS-only notification succeeds when Twilio is available"""
    mock_twilio = MagicMock()
    mock_twilio.send_sms = AsyncMock(return_value={"sid": "SM123", "status": "sent"})
    mock_twilio_cls.return_value = mock_twilio

    mock_email = MagicMock()
    mock_email_cls.return_value = mock_email

    payload = {
        "recipient_phone": "+1234567890",
        "message": "Test SMS message",
        "notification_type": "sms",
    }
    response = client.post("/functions/send_notification", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "sms" in data["data"]["channels"]
    assert "Notification sent successfully" in data["message"]

    mock_twilio.send_sms.assert_called_once()
    mock_email.send_email.assert_not_called()


@patch("src.functions.send_notification.EmailClient")
@patch("src.functions.send_notification.TwilioClient")
def test_send_notification_email_only_when_configured(mock_twilio_cls, mock_email_cls):
    """Email-only notification succeeds when SMTP is configured"""
    mock_email = MagicMock()
    mock_email.is_configured = True
    mock_email.send_email = AsyncMock(return_value={"status": "sent", "to": "test@example.com"})
    mock_email_cls.return_value = mock_email

    mock_twilio_cls.return_value = MagicMock()

    payload = {
        "recipient_phone": "+1234567890",
        "recipient_email": "test@example.com",
        "message": "Test email message",
        "notification_type": "email",
    }
    response = client.post("/functions/send_notification", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "email" in data["data"]["channels"]
    assert "Notification sent successfully" in data["message"]

    mock_email.send_email.assert_called_once()
    call_kwargs = mock_email.send_email.call_args[1]
    assert call_kwargs["to_email"] == "test@example.com"
    assert call_kwargs["body"] == "Test email message"


@patch("src.functions.send_notification.EmailClient")
@patch("src.functions.send_notification.TwilioClient")
def test_send_notification_email_only_when_smtp_not_configured(mock_twilio_cls, mock_email_cls):
    """Email-only with SMTP not configured returns failure"""
    mock_email = MagicMock()
    mock_email.is_configured = False
    mock_email_cls.return_value = mock_email

    mock_twilio_cls.return_value = MagicMock()

    payload = {
        "recipient_phone": "+1234567890",
        "recipient_email": "test@example.com",
        "message": "Test message",
        "notification_type": "email",
    }
    response = client.post("/functions/send_notification", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is False
    assert "SMTP not configured" in data["error"]
    assert data.get("data") is None or data.get("data", {}).get("channels", []) == []
    mock_email.send_email.assert_not_called()


@patch("src.functions.send_notification.EmailClient")
@patch("src.functions.send_notification.TwilioClient")
def test_send_notification_both_sms_and_email(mock_twilio_cls, mock_email_cls):
    """Both SMS and email succeed when both configured"""
    mock_twilio = MagicMock()
    mock_twilio.send_sms = AsyncMock(return_value={"sid": "SM456", "status": "sent"})
    mock_twilio_cls.return_value = mock_twilio

    mock_email = MagicMock()
    mock_email.is_configured = True
    mock_email.send_email = AsyncMock(return_value={"status": "sent", "to": "user@example.com"})
    mock_email_cls.return_value = mock_email

    payload = {
        "recipient_phone": "+1234567890",
        "recipient_email": "user@example.com",
        "message": "Test both channels",
        "notification_type": "both",
    }
    response = client.post("/functions/send_notification", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert set(data["data"]["channels"]) == {"sms", "email"}
    assert "Notification sent successfully" in data["message"]

    mock_twilio.send_sms.assert_called_once()
    mock_email.send_email.assert_called_once()


@patch("src.functions.send_notification.EmailClient")
@patch("src.functions.send_notification.TwilioClient")
def test_send_notification_both_with_sms_failure_email_succeeds(mock_twilio_cls, mock_email_cls):
    """When both requested, SMS fails but email succeeds - partial success"""
    from src.utils.errors import TwilioError

    mock_twilio = MagicMock()
    mock_twilio.send_sms = AsyncMock(side_effect=TwilioError("Twilio error", status_code=500))
    mock_twilio_cls.return_value = mock_twilio

    mock_email = MagicMock()
    mock_email.is_configured = True
    mock_email.send_email = AsyncMock(return_value={"status": "sent", "to": "user@example.com"})
    mock_email_cls.return_value = mock_email

    payload = {
        "recipient_phone": "+1234567890",
        "recipient_email": "user@example.com",
        "message": "Test partial",
        "notification_type": "both",
    }
    response = client.post("/functions/send_notification", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "email" in data["data"]["channels"]
    assert "sms" not in data["data"]["channels"]
    assert data["data"]["errors"] is not None
    assert any("SMS" in err or "Twilio" in err for err in data["data"]["errors"])


@patch("src.functions.send_notification.EmailClient")
@patch("src.functions.send_notification.TwilioClient")
def test_send_notification_default_notification_type_is_sms(mock_twilio_cls, mock_email_cls):
    """When notification_type omitted, defaults to SMS"""
    mock_twilio = MagicMock()
    mock_twilio.send_sms = AsyncMock(return_value={"sid": "SM789", "status": "sent"})
    mock_twilio_cls.return_value = mock_twilio

    mock_email_cls.return_value = MagicMock()

    payload = {
        "recipient_phone": "+1234567890",
        "message": "Default type test",
    }
    response = client.post("/functions/send_notification", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "sms" in data["data"]["channels"]
    assert data["data"]["notification_type"] == "sms"


def test_send_notification_validation_requires_recipient_phone():
    """Missing recipient_phone returns validation error"""
    payload = {
        "message": "No phone",
        "notification_type": "sms",
    }
    response = client.post("/functions/send_notification", json=payload)
    assert response.status_code == 422


def test_send_notification_validation_requires_message():
    """Missing message returns validation error"""
    payload = {
        "recipient_phone": "+1234567890",
        "notification_type": "sms",
    }
    response = client.post("/functions/send_notification", json=payload)
    assert response.status_code == 422
