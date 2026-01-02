from app.config import settings
from datetime import datetime, timezone
import logging

### Gmail SMTP
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

logger = logging.getLogger(__name__)

_snowflake_gen = None


def set_snowflake_generator(snowflake_gen):
    global _snowflake_gen
    _snowflake_gen = snowflake_gen


def snowflake_generator() -> int:
    if _snowflake_gen is None:
        raise Exception("SnowflakeGenerator is not initialized")
    return int(next(_snowflake_gen))


def get_timestamp():
    return int(datetime.now(timezone.utc).timestamp())


def send_email_via_smtp(to_email: str, subject: str, html_content: str, plain_text: str):
    """Send an email using Gmail SMTP server with TLS

    Returns:
        bool: True if successful, False otherwise
    """
    if not settings.FROM_EMAIL:
        logger.warning("FROM_EMAIL not configured. Skipping email.")
        return False

    if not settings.GMAIL_APP_PASSWORD:
        logger.warning("GMAIL_APP_PASSWORD not configured. Skipping email.")
        return False

    try:
        # Create message
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = settings.FROM_EMAIL
        message["To"] = to_email

        # Attach both plain text and HTML versions
        part1 = MIMEText(plain_text, "plain")
        part2 = MIMEText(html_content, "html")
        message.attach(part1)
        message.attach(part2)

        # Connect to Gmail SMTP server using TLS (port 587)
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()  # Upgrade to secure TLS connection
        server.login(settings.FROM_EMAIL, settings.GMAIL_APP_PASSWORD)
        server.sendmail(settings.FROM_EMAIL, to_email, message.as_string())
        server.quit()

        logger.info(f"Email sent successfully to {to_email}")
        return True

    except Exception as error:
        logger.error(f"Error sending email: {error}")
        return False


def send_reset_email(to_email: str, subject: str, reset_link: str):
    """Send a password reset email via Gmail SMTP

    Returns:
        bool: True if successful, False otherwise
    """
    if not settings.FROM_EMAIL or not settings.GMAIL_APP_PASSWORD:
        logger.warning(
            f"Email configuration incomplete. FROM_EMAIL: {'set' if settings.FROM_EMAIL else 'missing'}, "
            f"GMAIL_APP_PASSWORD: {'set' if settings.GMAIL_APP_PASSWORD else 'missing'}"
        )
        return False

    plain_text = f"Reset your password: {reset_link}"
    html_content = f"""
    <html>
        <body>
            <p>點選以下連結來重置你的密碼, 請在 {settings.RESET_TOKEN_EXPIRE_MINUTES} 分鐘內完成</p>
            <p>
                <a href="{reset_link}" style="
                    padding: 10px 20px;
                    background-color: #007BFF;
                    color: white;
                    text-decoration: none;
                    border-radius: 4px;
                    display: inline-block;
                ">重製密碼</a>
            </p>
        </body>
    </html>
    """

    result = send_email_via_smtp(to_email, subject, html_content, plain_text)
    if result:
        logger.info(f"Password reset email sent to {to_email}")
    else:
        logger.error(f"Failed to send password reset email to {to_email}")
    return result


def send_verification_email(to_email: str, subject: str, verification_link: str):
    """Send a verification email via Gmail SMTP

    Returns:
        bool: True if successful, False otherwise
    """
    if not settings.FROM_EMAIL or not settings.GMAIL_APP_PASSWORD:
        logger.warning(
            f"Email configuration incomplete. FROM_EMAIL: {'set' if settings.FROM_EMAIL else 'missing'}, "
            f"GMAIL_APP_PASSWORD: {'set' if settings.GMAIL_APP_PASSWORD else 'missing'}"
        )
        return False

    plain_text = f"Verify your email: {verification_link}"
    html_content = f"""
    <html>
        <body>
            <h2>歡迎註冊!</h2>
            <p>請點選以下連結來驗證你的電子郵件地址:</p>
            <p>
                <a href="{verification_link}" style="
                    padding: 10px 20px;
                    background-color: #28a745;
                    color: white;
                    text-decoration: none;
                    border-radius: 4px;
                    display: inline-block;
                ">驗證電子郵件</a>
            </p>
            <p>此連結將在 24 小時內有效。</p>
        </body>
    </html>
    """

    result = send_email_via_smtp(to_email, subject, html_content, plain_text)
    if result:
        logger.info(f"Verification email sent to {to_email}")
    else:
        logger.error(f"Failed to send verification email to {to_email}")
    return result