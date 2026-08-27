import logging
from email.message import EmailMessage
from urllib.parse import urlencode

import aiosmtplib

from app.core.config import settings
from app.core.tokens import generate_email_verification_token, generate_password_reset_token

logger = logging.getLogger(__name__)


async def send_email(to: str, subject: str, plain_body: str, html_body: str) -> None:
    """Hand one message to the configured SMTP server.

    Text and HTML parts are both attached: clients that can't render HTML fall back to
    the text, which also keeps the message out of spam folders more reliably.
    """
    message = EmailMessage()
    message["From"] = f"{settings.mail_from_name} <{settings.mail_from}>"
    message["To"] = to
    message["Subject"] = subject
    message.set_content(plain_body)
    message.add_alternative(html_body, subtype="html")

    try:
        await aiosmtplib.send(
            message,
            hostname=settings.mail_host,
            port=settings.mail_port,
            start_tls=settings.mail_use_tls or None,
            username=settings.mail_username or None,
            password=settings.mail_password or None,
        )
    except Exception as exc:
        # Runs in a background task, after the response has gone, so raising would only
        # produce a contextless traceback. The user can request a new link instead.
        #
        # The cause goes on the message line, not just in the traceback: log viewers
        # filter by line, and a bare "failed to send" is not worth reading.
        logger.exception(
            "Failed to send email to %s via %s:%s as %r - %s: %s",
            to,
            settings.mail_host,
            settings.mail_port,
            settings.mail_username,
            type(exc).__name__,
            exc,
        )


async def send_verification_email(to: str, username: str) -> None:
    """Send the "confirm your address" message for a newly registered account."""
    token = generate_email_verification_token(to)
    link = f"{settings.verification_url_base}?{urlencode({'token': token})}"
    hours = settings.email_verification_expire_hours

    plain_body = (
        f"Hi {username},\n\n"
        "Welcome to GamerZone! Confirm your email address to unlock the members area:\n\n"
        f"{link}\n\n"
        f"This link expires in {hours} hours.\n"
        "If you didn't create this account, you can ignore this message.\n"
    )

    html_body = f"""\
<html>
  <body style="font-family: system-ui, sans-serif; line-height: 1.6; color: #e5e5e5;
               background: #111; padding: 32px;">
    <h2 style="color: #fff; margin-top: 0;">Welcome to GamerZone, {username}!</h2>
    <p>Confirm your email address to unlock the members area and download links.</p>
    <p style="margin: 28px 0;">
      <a href="{link}"
         style="background: #6d28d9; color: #fff; padding: 12px 22px;
                border-radius: 8px; text-decoration: none; font-weight: 600;">
        Verify my email
      </a>
    </p>
    <p style="color: #9a9a9a; font-size: 14px;">
      This link expires in {hours} hours. If you didn't create this account,
      you can safely ignore this email.
    </p>
  </body>
</html>
"""

    await send_email(
        to=to,
        subject="Verify your GamerZone account",
        plain_body=plain_body,
        html_body=html_body,
    )


async def send_password_reset_email(to: str, username: str, hashed_password: str) -> None:
    """Send the password-reset message.

    The password hash goes in only as a fingerprint inside the token, so the link stops
    working the moment the password actually changes.
    """
    token = generate_password_reset_token(to, hashed_password)
    link = f"{settings.password_reset_url_base}?{urlencode({'token': token})}"
    minutes = settings.password_reset_expire_minutes

    plain_body = (
        f"Hi {username},\n\n"
        "Someone asked to reset the password for your GamerZone account. "
        "Use the link below to choose a new one:\n\n"
        f"{link}\n\n"
        f"This link expires in {minutes} minutes and can only be used once.\n"
        "If this wasn't you, ignore this email - your password stays unchanged.\n"
    )

    html_body = f"""\
<html>
  <body style="font-family: system-ui, sans-serif; line-height: 1.6; color: #e5e5e5;
               background: #111; padding: 32px;">
    <h2 style="color: #fff; margin-top: 0;">Reset your password</h2>
    <p>Hi {username}, someone asked to reset the password for your GamerZone account.</p>
    <p style="margin: 28px 0;">
      <a href="{link}"
         style="background: #6d28d9; color: #fff; padding: 12px 22px;
                border-radius: 8px; text-decoration: none; font-weight: 600;">
        Choose a new password
      </a>
    </p>
    <p style="color: #9a9a9a; font-size: 14px;">
      This link expires in {minutes} minutes and can only be used once.
      If this wasn't you, you can ignore this email - your password stays unchanged.
    </p>
  </body>
</html>
"""

    await send_email(
        to=to,
        subject="Reset your GamerZone password",
        plain_body=plain_body,
        html_body=html_body,
    )
