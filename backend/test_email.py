#!/usr/bin/env python3
"""
Test script to verify Gmail SMTP configuration

=============================================================================
USAGE INSTRUCTIONS
=============================================================================

1. SETUP GMAIL APP PASSWORD:
   - Enable 2FA: https://myaccount.google.com/security
   - Generate App Password: https://myaccount.google.com/apppasswords
   - Select "Mail" and your device
   - Copy the 16-character password (no spaces)

2. CONFIGURE .ENV FILE:
   Edit the .env file in the project root directory:

   FROM_EMAIL=your-email@gmail.com
   GMAIL_APP_PASSWORD=abcdabcdabcdabcd  # 16 chars, no spaces

3. RUN THE TEST:
   From the backend directory:

   cd backend
   python test_email.py recipient@example.com

   OR from project root:

   python backend/test_email.py recipient@example.com

4. EXPECTED OUTPUT:
   - Shows configuration status (FROM_EMAIL, GMAIL_APP_PASSWORD)
   - Attempts to send test email
   - Reports success or failure with error details

5. TROUBLESHOOTING:
   - "Authentication failed": Regenerate App Password
   - "Configuration incomplete": Check .env file values
   - ".env not found": Create from .env.template
   - "Connection refused": Check firewall/network on port 587

=============================================================================

Example:
    $ cd backend
    $ python test_email.py myemail@example.com

    Loaded environment from: /home/user/project/.env

    ==================================================
    Gmail SMTP Configuration Test
    ==================================================

    1. Checking environment variables...
       FROM_EMAIL: ✓ Set
       Email address: sender@gmail.com
       GMAIL_APP_PASSWORD: ✓ Set
       Password preview: abcd********wxyz

    ✓ Configuration looks good!

    2. Sending test email to myemail@example.com...

    ✓ Email sent successfully!
      Check myemail@example.com inbox for the test email

    ==================================================
"""

import sys
import os
from pathlib import Path

# Add project root to path
backend_dir = Path(__file__).parent
project_root = backend_dir.parent
sys.path.insert(0, str(backend_dir))
sys.path.insert(0, str(project_root))

# Load .env file explicitly
from dotenv import load_dotenv
env_path = project_root / ".env"
if env_path.exists():
    load_dotenv(env_path)
    print(f"Loaded environment from: {env_path}")
else:
    print(f"Warning: .env file not found at {env_path}")
    print()
    print("To fix this:")
    print("  1. Copy the template: cp .env.template .env")
    print("  2. Edit .env and add your Gmail credentials")
    print()
    sys.exit(1)

from app.config import settings
from app.utils import send_email_via_smtp


def test_email_config():
    """Test email configuration"""
    print()
    print("=" * 50)
    print("Gmail SMTP Configuration Test")
    print("=" * 50)
    print()

    # Check configuration
    print("1. Checking environment variables...")
    print(f"   FROM_EMAIL: {'✓ Set' if settings.FROM_EMAIL else '✗ Missing'}")
    if settings.FROM_EMAIL:
        print(f"   Email address: {settings.FROM_EMAIL}")

    print(f"   GMAIL_APP_PASSWORD: {'✓ Set' if settings.GMAIL_APP_PASSWORD else '✗ Missing'}")
    if settings.GMAIL_APP_PASSWORD:
        password_preview = settings.GMAIL_APP_PASSWORD[:4] + "*" * 8 + settings.GMAIL_APP_PASSWORD[-4:]
        print(f"   Password preview: {password_preview}")

    print()

    if not settings.FROM_EMAIL or not settings.GMAIL_APP_PASSWORD:
        print("❌ Email configuration is incomplete!")
        print()
        print("To fix this:")
        print("1. Edit your .env file")
        print("2. Set FROM_EMAIL to your Gmail address")
        print("3. Generate an App Password at https://myaccount.google.com/apppasswords")
        print("4. Set GMAIL_APP_PASSWORD to your 16-character App Password")
        print()
        print("Example .env configuration:")
        print("  FROM_EMAIL=your-email@gmail.com")
        print("  GMAIL_APP_PASSWORD=abcdabcdabcdabcd")
        print()
        return False

    print("✓ Configuration looks good!")
    print()

    # Get recipient email
    if len(sys.argv) < 2:
        print("Usage: python test_email.py recipient@example.com")
        print()
        print("Example:")
        print("  python test_email.py myemail@example.com")
        print()
        return False

    recipient = sys.argv[1]

    # Validate email format (basic check)
    if "@" not in recipient or "." not in recipient.split("@")[-1]:
        print(f"❌ Invalid email address: {recipient}")
        print()
        return False

    # Send test email
    print(f"2. Sending test email to {recipient}...")

    subject = "Test Email from RAG Chat Application"
    plain_text = "This is a test email to verify Gmail SMTP configuration."
    html_content = """
    <html>
        <body>
            <h2>Test Email</h2>
            <p>This is a test email to verify Gmail SMTP configuration.</p>
            <p>If you received this email, your SMTP setup is working correctly! ✓</p>
            <hr>
            <p style="color: #666; font-size: 12px;">
                Sent from: RAG Chat Application<br>
                SMTP Server: smtp.gmail.com:587 (TLS)
            </p>
        </body>
    </html>
    """

    result = send_email_via_smtp(recipient, subject, html_content, plain_text)

    print()
    if result:
        print("✓ Email sent successfully!")
        print(f"  Check {recipient} inbox for the test email")
        print()
        print("Note: If you don't see the email:")
        print("  - Check spam/junk folder")
        print("  - Wait a few minutes for delivery")
        print("  - Verify the recipient email is correct")
    else:
        print("✗ Failed to send email")
        print()
        print("Common issues:")
        print("  - Invalid App Password (regenerate at https://myaccount.google.com/apppasswords)")
        print("  - 2FA not enabled on Google account")
        print("  - Network/firewall blocking port 587")
        print("  - Incorrect Gmail address in FROM_EMAIL")
        print()
        print("Check the error message above for more details")

    print()
    print("=" * 50)
    return result


if __name__ == "__main__":
    success = test_email_config()
    sys.exit(0 if success else 1)
