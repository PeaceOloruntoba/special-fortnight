import httpx
from app.config import settings
from fastapi import HTTPException, status
import logging

logger = logging.getLogger(__name__)

async def send_brevo_email(to_email: str, subject: str, html_content: str):
    url = "https://api.brevo.com/v3/smtp/email"
    headers = {
        "accept": "application/json",
        "api-key": settings.BREVO_API_KEY,
        "content-type": "application/json",
    }
    payload = {
        "sender": {"name": settings.EMAIL_FROM_NAME, "email": settings.EMAIL_FROM_EMAIL},
        "to": [{"email": to_email}],
        "subject": subject,
        "htmlContent": html_content,
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)
            logger.info(f"Email sent successfully to {to_email}. Response: {response.json()}")
            return response.json()
        except httpx.RequestError as e:
            logger.error(f"An error occurred while sending email to {to_email}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to send email: {e}"
            )
        except httpx.HTTPStatusError as e:
            logger.error(f"Brevo API error for {to_email}: {e.response.status_code} - {e.response.text}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Brevo API error: {e.response.text}"
            )

async def send_verification_email(to_email: str, recipient_name: str, verification_link: str):
    subject = "Verify Your E-Wallet Account"
    html_content = f"""
    <html>
    <body>
        <p>Hello {recipient_name},</p>
        <p>Thank you for registering with E-Wallet! To activate your account and start managing your finances, please click on the link below:</p>
        <p><a href="{verification_link}">Verify Your Email Address</a></p>
        <p>If you did not register for this account, please ignore this email.</p>
        <p>Best regards,</p>
        <p>The E-Wallet Team</p>
    </body>
    </html>
    """
    await send_brevo_email(to_email, subject, html_content)

# You can add other email functions like:
async def send_password_reset_email(to_email: str, recipient_name: str, reset_link: str):
    subject = "E-Wallet Password Reset Request"
    html_content = f"""
    <html>
    <body>
        <p>Hello {recipient_name},</p>
        <p>We received a request to reset your password for your E-Wallet account. If you made this request, please click on the link below to reset your password:</p>
        <p><a href="{reset_link}">Reset Your Password</a></p>
        <p>If you did not request a password reset, please ignore this email.</p>
        <p>This link will expire in [e.g., 1 hour].</p>
        <p>Best regards,</p>
        <p>The E-Wallet Team</p>
    </body>
    </html>
    """
    await send_brevo_email(to_email, subject, html_content)
