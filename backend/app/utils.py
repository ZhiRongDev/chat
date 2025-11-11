import redis
from app.config import settings
from datetime import datetime, timezone

### Gmail email API
import os
import base64
from email.message import EmailMessage
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

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


def get_gmail_credentials():
    """Load or refresh OAuth2 credentials from token.json"""
    creds = None
    if os.path.exists(settings.TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(
            settings.TOKEN_FILE, settings.SCOPES
        )

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                settings.CREDENTIALS_FILE, settings.SCOPES
            )
            creds = flow.run_local_server(port=0)
        with open(settings.TOKEN_FILE, "w") as token:
            token.write(creds.to_json())

    return creds


def send_reset_email(to_email: str, subject: str, reset_link: str):
    """Send an email with HTML content via Gmail API using OAuth2"""
    creds = get_gmail_credentials()

    try:
        service = build("gmail", "v1", credentials=creds)

        # Create message with both text and HTML versions
        message = EmailMessage()
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

        message.set_content(plain_text)
        message.add_alternative(html_content, subtype="html")

        message["To"] = to_email
        message["From"] = settings.FROM_EMAIL
        message["Subject"] = subject

        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        create_message = {"raw": encoded_message}

        send_result = (
            service.users().messages().send(userId="me", body=create_message).execute()
        )
        print(f"✅ Message sent. ID: {send_result['id']}")
        return send_result

    except HttpError as error:
        print(f"❌ An error occurred: {error}")
        return None


def send_verification_email(to_email: str, subject: str, verification_link: str):
    """Send a verification email via Gmail API using OAuth2"""
    creds = get_gmail_credentials()

    try:
        service = build("gmail", "v1", credentials=creds)

        # Create message with both text and HTML versions
        message = EmailMessage()
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

        message.set_content(plain_text)
        message.add_alternative(html_content, subtype="html")

        message["To"] = to_email
        message["From"] = settings.FROM_EMAIL
        message["Subject"] = subject

        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        create_message = {"raw": encoded_message}

        send_result = (
            service.users().messages().send(userId="me", body=create_message).execute()
        )
        print(f"✅ Verification email sent. ID: {send_result['id']}")
        return send_result

    except HttpError as error:
        print(f"❌ An error occurred: {error}")
        return None