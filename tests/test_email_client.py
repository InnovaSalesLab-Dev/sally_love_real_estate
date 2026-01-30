"""
Unit tests for EmailClient (SMTP)
"""

import pytest
from unittest.mock import patch, MagicMock

from src.integrations.email_client import EmailClient, _send_email_sync
from src.utils.errors import EmailError


# ---------------------------------------------------------------------------
# EmailClient unit tests
# ---------------------------------------------------------------------------


@patch("src.integrations.email_client.settings")
def test_email_client_is_configured_true(mock_settings):
    """is_configured returns True when all required SMTP vars are set"""
    mock_settings.SMTP_HOST = "smtp.example.com"
    mock_settings.SMTP_USERNAME = "user"
    mock_settings.SMTP_PASSWORD = "secret"
    client = EmailClient()
    assert client.is_configured is True


@patch("src.integrations.email_client.settings")
def test_email_client_is_configured_false_when_host_missing(mock_settings):
    """is_configured returns False when SMTP_HOST is empty"""
    mock_settings.SMTP_HOST = ""
    mock_settings.SMTP_USERNAME = "user"
    mock_settings.SMTP_PASSWORD = "secret"
    client = EmailClient()
    assert client.is_configured is False


@patch("src.integrations.email_client.settings")
def test_email_client_is_configured_false_when_username_missing(mock_settings):
    """is_configured returns False when SMTP_USERNAME is empty"""
    mock_settings.SMTP_HOST = "smtp.example.com"
    mock_settings.SMTP_USERNAME = ""
    mock_settings.SMTP_PASSWORD = "secret"
    client = EmailClient()
    assert client.is_configured is False


@patch("src.integrations.email_client.settings")
def test_email_client_is_configured_false_when_password_missing(mock_settings):
    """is_configured returns False when SMTP_PASSWORD is empty"""
    mock_settings.SMTP_HOST = "smtp.example.com"
    mock_settings.SMTP_USERNAME = "user"
    mock_settings.SMTP_PASSWORD = ""
    client = EmailClient()
    assert client.is_configured is False


@pytest.mark.asyncio
@patch("src.integrations.email_client.settings")
async def test_send_email_raises_when_not_configured(mock_settings):
    """send_email raises EmailError when SMTP not configured"""
    mock_settings.SMTP_HOST = ""
    mock_settings.SMTP_USERNAME = ""
    mock_settings.SMTP_PASSWORD = ""
    client = EmailClient()

    with pytest.raises(EmailError) as exc_info:
        await client.send_email(
            to_email="test@example.com",
            subject="Test",
            body="Body",
        )
    assert "not configured" in str(exc_info.value.message).lower()


@pytest.mark.asyncio
@patch("src.integrations.email_client._send_email_sync")
@patch("src.integrations.email_client.settings")
async def test_send_email_success(mock_settings, mock_sync_send):
    """send_email delegates to _send_email_sync and returns result"""
    mock_settings.SMTP_HOST = "smtp.example.com"
    mock_settings.SMTP_USERNAME = "user"
    mock_settings.SMTP_PASSWORD = "secret"
    mock_sync_send.return_value = {"status": "sent", "to": "test@example.com", "subject": "Hi"}

    client = EmailClient()
    result = await client.send_email(
        to_email="test@example.com",
        subject="Hi",
        body="Hello",
        html_body="<p>Hello</p>",
    )

    assert result == {"status": "sent", "to": "test@example.com", "subject": "Hi"}
    mock_sync_send.assert_called_once_with(
        to_email="test@example.com",
        subject="Hi",
        body="Hello",
        html_body="<p>Hello</p>",
    )


# ---------------------------------------------------------------------------
# _send_email_sync unit tests (mocked smtplib)
# ---------------------------------------------------------------------------


@patch("src.integrations.email_client.settings")
def test_send_email_sync_raises_when_host_missing(mock_settings):
    """_send_email_sync raises when SMTP_HOST not set"""
    mock_settings.SMTP_HOST = ""
    mock_settings.SMTP_PORT = 587
    mock_settings.SMTP_USERNAME = "user"
    mock_settings.SMTP_PASSWORD = "pass"
    mock_settings.SMTP_FROM_EMAIL = ""
    mock_settings.SMTP_USE_TLS = True

    with pytest.raises(EmailError) as exc_info:
        _send_email_sync(to_email="x@y.com", subject="S", body="B")
    assert "not configured" in str(exc_info.value.message).lower()


@patch("src.integrations.email_client.smtplib.SMTP")
@patch("src.integrations.email_client.settings")
def test_send_email_sync_success_starttls(mock_settings, mock_smtp):
    """_send_email_sync sends via SMTP with STARTTLS on port 587"""
    mock_settings.SMTP_HOST = "smtp.example.com"
    mock_settings.SMTP_PORT = 587
    mock_settings.SMTP_USERNAME = "user@example.com"
    mock_settings.SMTP_PASSWORD = "secret"
    mock_settings.SMTP_FROM_EMAIL = "from@example.com"
    mock_settings.SMTP_USE_TLS = True

    mock_server = MagicMock()
    mock_smtp.return_value.__enter__.return_value = mock_server

    result = _send_email_sync(
        to_email="recipient@example.com",
        subject="Test Subject",
        body="Plain body",
        html_body="<p>HTML body</p>",
    )

    assert result["status"] == "sent"
    assert result["to"] == "recipient@example.com"
    assert result["subject"] == "Test Subject"
    mock_server.starttls.assert_called_once()
    mock_server.login.assert_called_once_with("user@example.com", "secret")
    mock_server.sendmail.assert_called_once()
    call_args = mock_server.sendmail.call_args[0]
    assert call_args[0] == "from@example.com"
    assert call_args[1] == ["recipient@example.com"]


@patch("src.integrations.email_client.smtplib.SMTP_SSL")
@patch("src.integrations.email_client.settings")
def test_send_email_sync_uses_ssl_on_port_465(mock_settings, mock_smtp_ssl):
    """_send_email_sync uses SMTP_SSL when port is 465"""
    mock_settings.SMTP_HOST = "smtp.example.com"
    mock_settings.SMTP_PORT = 465
    mock_settings.SMTP_USERNAME = "user"
    mock_settings.SMTP_PASSWORD = "pass"
    mock_settings.SMTP_FROM_EMAIL = "from@example.com"
    mock_settings.SMTP_USE_TLS = True

    mock_server = MagicMock()
    mock_smtp_ssl.return_value.__enter__.return_value = mock_server

    result = _send_email_sync(to_email="r@x.com", subject="S", body="B")

    assert result["status"] == "sent"
    mock_smtp_ssl.assert_called_once_with("smtp.example.com", 465, timeout=30)
    mock_server.starttls.assert_not_called()
