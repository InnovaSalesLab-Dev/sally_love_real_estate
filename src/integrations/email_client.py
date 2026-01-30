"""
SMTP email client for sending notifications
"""

import asyncio
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Dict, Any, Optional

from src.config.settings import settings
from src.utils.logger import get_logger
from src.utils.errors import EmailError

logger = get_logger(__name__)


def _send_email_sync(
    to_email: str,
    subject: str,
    body: str,
    html_body: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Synchronous SMTP send - called via asyncio.to_thread.
    """
    host = settings.SMTP_HOST
    port = settings.SMTP_PORT
    username = settings.SMTP_USERNAME
    password = settings.SMTP_PASSWORD
    from_email = settings.SMTP_FROM_EMAIL or username
    use_tls = settings.SMTP_USE_TLS

    if not host or not username or not password:
        raise EmailError(
            message="SMTP not configured (SMTP_HOST, SMTP_USERNAME, SMTP_PASSWORD required)",
            status_code=500,
            details={"host_set": bool(host), "username_set": bool(username), "password_set": bool(password)},
        )

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = from_email
    msg["To"] = to_email

    msg.attach(MIMEText(body, "plain"))
    if html_body:
        msg.attach(MIMEText(html_body, "html"))

    smtp_class = smtplib.SMTP_SSL if port == 465 else smtplib.SMTP
    try:
        with smtp_class(host, port, timeout=30) as server:
            if use_tls and port != 465:
                server.starttls()
            if username and password:
                server.login(username, password)
            server.sendmail(from_email, [to_email], msg.as_string())
    except smtplib.SMTPAuthenticationError as e:
        raise EmailError(
            message=f"SMTP authentication failed: {e}",
            status_code=401,
            details={"error": str(e)},
        )
    except smtplib.SMTPException as e:
        raise EmailError(
            message=f"SMTP error: {e}",
            status_code=500,
            details={"error": str(e)},
        )
    except Exception as e:
        raise EmailError(
            message=f"Failed to send email: {e}",
            status_code=500,
            details={"error": str(e)},
        )

    return {"status": "sent", "to": to_email, "subject": subject}


class EmailClient:
    """Async client for sending email via SMTP"""

    def __init__(self) -> None:
        self.host = settings.SMTP_HOST
        self.username = settings.SMTP_USERNAME
        self.password = settings.SMTP_PASSWORD

    @property
    def is_configured(self) -> bool:
        """Check if SMTP is properly configured"""
        return bool(self.host and self.username and self.password)

    async def send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        html_body: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Send an email via SMTP.

        Args:
            to_email: Recipient email address
            subject: Email subject line
            body: Plain text body
            html_body: Optional HTML body

        Returns:
            Dict with status, to, subject

        Raises:
            EmailError: If email fails to send
        """
        if not self.is_configured:
            raise EmailError(
                message="SMTP not configured (SMTP_HOST, SMTP_USERNAME, SMTP_PASSWORD required)",
                status_code=500,
                details={"host_set": bool(self.host), "username_set": bool(self.username)},
            )

        return await asyncio.to_thread(
            _send_email_sync,
            to_email=to_email,
            subject=subject,
            body=body,
            html_body=html_body,
        )
