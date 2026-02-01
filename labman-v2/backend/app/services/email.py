import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from app.config import get_settings
import asyncio
from sqlalchemy.orm import Session
from app.models import EmailFailure
from datetime import datetime

settings = get_settings()

async def send_email(
    to_email: str,
    subject: str,
    body_html: str,
    body_text: Optional[str] = None
) -> bool:
    """Send an email"""
    if not settings.SMTP_HOST:
        print(f"SMTP not configured, skipping email to {to_email}")
        return False
    
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = settings.EMAILS_FROM_EMAIL or settings.SMTP_USER
        msg['To'] = to_email
        
        if body_text:
            part1 = MIMEText(body_text, 'plain')
            msg.attach(part1)
        
        part2 = MIMEText(body_html, 'html')
        msg.attach(part2)
        
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            if settings.SMTP_TLS:
                server.starttls()
            if settings.SMTP_USER and settings.SMTP_PASSWORD:
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.send_message(msg)
        
        return True
    except Exception as e:
        print(f"Failed to send email to {to_email}: {e}")
        return False

async def send_activation_email(to_email: str, name: str, activation_link: str) -> bool:
    """Send account activation email"""
    subject = "Activate Your Account"
    body_html = f"""
    <html>
        <body>
            <h2>Welcome to LabMan!</h2>
            <p>Hi {name},</p>
            <p>Your account has been created. Please click the link below to activate your account and set your password:</p>
            <p><a href="{activation_link}">Activate Account</a></p>
            <p>This link will expire in 24 hours.</p>
        </body>
    </html>
    """
    body_text = f"Hi {name},\n\nActivate your account: {activation_link}"
    
    return await send_email(to_email, subject, body_html, body_text)

async def send_password_reset_email(to_email: str, name: str, reset_link: str) -> bool:
    """Send password reset email"""
    subject = "Reset Your Password"
    body_html = f"""
    <html>
        <body>
            <h2>Password Reset Request</h2>
            <p>Hi {name},</p>
            <p>Click the link below to reset your password:</p>
            <p><a href="{reset_link}">Reset Password</a></p>
            <p>This link will expire in 24 hours.</p>
        </body>
    </html>
    """
    body_text = f"Hi {name},\n\nReset your password: {reset_link}"
    
    return await send_email(to_email, subject, body_html, body_text)

async def send_meeting_notification(
    to_email: str,
    name: str,
    meeting_title: str,
    meeting_time: str,
    meeting_link: str
) -> bool:
    """Send meeting notification email"""
    subject = f"Meeting: {meeting_title}"
    body_html = f"""
    <html>
        <body>
            <h2>Meeting Notification</h2>
            <p>Hi {name},</p>
            <p>You have been invited to a meeting:</p>
            <p><strong>{meeting_title}</strong></p>
            <p>Time: {meeting_time}</p>
            <p><a href="{meeting_link}">View Meeting Details</a></p>
        </body>
    </html>
    """
    body_text = f"Hi {name},\n\nMeeting: {meeting_title}\nTime: {meeting_time}\n{meeting_link}"
    
    return await send_email(to_email, subject, body_html, body_text)
