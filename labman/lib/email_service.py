"""
Centralized email service for Lab Manager application.

This module provides email functionality with retry mechanisms,
template rendering, and integration with the background email queue.
"""
import smtplib
import time
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from functools import wraps
from typing import Optional, Dict, Any, List
from labman.lib.helpers import get_smtp_config, get_lab_name, get_server_url, is_email_configured

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def retry_on_failure(max_attempts: int = 3, delay: int = 1):
    """
    Decorator to retry email sending on failure with exponential backoff.
    
    Args:
        max_attempts: Maximum number of retry attempts
        delay: Initial delay in seconds between retries
        
    Returns:
        Decorated function with retry logic
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts - 1:
                        # Final attempt failed, log it
                        logger.error(f"Email failed after {max_attempts} attempts: {func.__name__} - {e}")
                        _log_email_failure(func.__name__, str(e), args, kwargs)
                        return False
                    
                    # Exponential backoff
                    wait_time = delay * (2 ** attempt)
                    logger.warning(f"Email attempt {attempt + 1} failed, retrying in {wait_time}s: {e}")
                    time.sleep(wait_time)
            
            return False
        return wrapper
    return decorator


def _log_email_failure(func_name: str, error: str, args: tuple, kwargs: dict):
    """
    Log email failure to database for later retry.
    
    Args:
        func_name: Name of the email function that failed
        error: Error message
        args: Function arguments
        kwargs: Function keyword arguments
    """
    try:
        from labman.lib.data import execute_db
        import json
        
        # Extract recipient if available
        recipient = kwargs.get('email', kwargs.get('recipient', {}).get('email', 'unknown'))
        
        # Store payload as JSON
        payload = json.dumps({
            'args': str(args),
            'kwargs': {k: str(v) for k, v in kwargs.items()}
        })
        
        execute_db('''
            INSERT INTO email_failures (email_type, recipient, error_message, payload)
            VALUES (?, ?, ?, ?)
        ''', (func_name, recipient, error, payload))
        
        logger.info(f"Logged email failure for {recipient}")
    except Exception as e:
        logger.error(f"Failed to log email failure: {e}")


def _send_email(to_email: str, subject: str, text_body: str, html_body: str, cc_emails: Optional[List[str]] = None) -> bool:
    """
    Internal function to send email via SMTP.
    
    Args:
        to_email: Recipient email address
        subject: Email subject
        text_body: Plain text email body
        html_body: HTML email body
        cc_emails: Optional list of CC recipient email addresses
        
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    if not is_email_configured():
        logger.warning("Email not configured, skipping send")
        return False
    
    config = get_smtp_config()
    
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = config['sender_email']
        msg['To'] = to_email
        
        all_recipients = [to_email]
        if cc_emails:
            msg['Cc'] = ', '.join(cc_emails)
            all_recipients.extend(cc_emails)
        
        # Attach both plain text and HTML versions
        part1 = MIMEText(text_body, 'plain')
        part2 = MIMEText(html_body, 'html')
        msg.attach(part1)
        msg.attach(part2)
        
        # Send email
        with smtplib.SMTP(config['server'], config['port']) as server:
            server.starttls()
            server.login(config['username'], config['password'])
            server.send_message(msg)
        
        logger.info(f"Email sent successfully to {to_email} (CC: {cc_emails})")
        return True
        
    except Exception as e:
        logger.error(f"SMTP error sending to {to_email}: {e}")
        raise  # Re-raise to trigger retry mechanism


def _render_email_template(template_name: str, **context) -> tuple:
    """
    Render email template with given context.
    
    Args:
        template_name: Name of the template
        **context: Template context variables
        
    Returns:
        tuple: (text_body, html_body)
    """
    lab_name = get_lab_name()
    server_url = get_server_url()
    
    # Add common context
    context['lab_name'] = lab_name
    context['server_url'] = server_url
    
    # Template rendering based on template name
    if template_name == 'activation':
        return _render_activation_template(**context)
    elif template_name == 'password_reset':
        return _render_password_reset_template(**context)
    elif template_name == 'email_verification':
        return _render_email_verification_template(**context)
    elif template_name == 'meeting_notification':
        return _render_meeting_notification_template(**context)
    elif template_name == 'meeting_update':
        return _render_meeting_update_template(**context)
    elif template_name == 'content_notification':
        return _render_content_notification_template(**context)
    else:
        raise ValueError(f"Unknown template: {template_name}")


# Template rendering functions
def _render_activation_template(name: str, activation_link: str, lab_name: str, **kwargs) -> tuple:
    """Render account activation email template"""
    text = f"""
Hello {name},

Your account has been created for the {lab_name} Management System.

Please activate your account and set your password by clicking the link below:
{activation_link}

This link will expire in 24 hours.

Best regards,
{lab_name} Team
"""
    
    html = f"""
<html>
<body style="font-family: 'Nunito', Arial, sans-serif; line-height: 1.6; color: #3E2723;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
        <h2 style="color: #8B4513;">Welcome to {lab_name}!</h2>
        <p>Hello {name},</p>
        <p>Your account has been created for the {lab_name} Management System.</p>
        <p>Please activate your account and set your password:</p>
        <div style="margin: 30px 0;">
            <a href="{activation_link}" 
               style="background-color: #8B4513; color: white; padding: 12px 30px; 
                      text-decoration: none; border-radius: 4px; display: inline-block;">
                Activate Account
            </a>
        </div>
        <p style="color: #6D4C41; font-size: 14px;">
            This link will expire in 24 hours.
        </p>
        <hr style="border: none; border-top: 1px solid #BCAAA4; margin: 30px 0;">
        <p style="color: #6D4C41; font-size: 12px;">
            Best regards,<br>
            {lab_name} Team<br>
        </p>
    </div>
</body>
</html>
"""
    return (text, html)


def _render_password_reset_template(name: str, reset_link: str, lab_name: str, **kwargs) -> tuple:
    """Render password reset email template"""
    text = f"""
Hello {name},

You have requested to reset your password for {lab_name} Management System.

Click the link below to reset your password:
{reset_link}

This link will expire in 24 hours.

If you did not request this reset, please ignore this email.

Best regards,
{lab_name} Team
"""
    
    html = f"""
<html>
<body style="font-family: 'Nunito', Arial, sans-serif; line-height: 1.6; color: #3E2723;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
        <h2 style="color: #8B4513;">Password Reset Request</h2>
        <p>Hello {name},</p>
        <p>You have requested to reset your password for {lab_name} Management System.</p>
        <p>Click the button below to reset your password:</p>
        <div style="margin: 30px 0;">
            <a href="{reset_link}" 
               style="background-color: #8B4513; color: white; padding: 12px 30px; 
                      text-decoration: none; border-radius: 4px; display: inline-block;">
                Reset Password
            </a>
        </div>
        <p style="color: #6D4C41; font-size: 14px;">
            This link will expire in 24 hours.
        </p>
        <p style="color: #6D4C41; font-size: 14px;">
            If you did not request this reset, please ignore this email.
        </p>
        <hr style="border: none; border-top: 1px solid #BCAAA4; margin: 30px 0;">
        <p style="color: #6D4C41; font-size: 12px;">
            Best regards,<br>
            {lab_name} Team<br>
        </p>
    </div>
</body>
</html>
"""
    return (text, html)


def _render_email_verification_template(name: str, email: str, verification_link: str, lab_name: str, **kwargs) -> tuple:
    """Render email verification template"""
    text = f"""
Hello {name},

You requested to change your email address to: {email}

Click the link below to verify this email address:
{verification_link}

This link will expire in 24 hours.

Best regards,
{lab_name} Team
"""
    
    html = f"""
<html>
<body style="font-family: 'Nunito', Arial, sans-serif; color: #3E2723;">
    <h2 style="color: #8B4513;">Verify Your Email Change</h2>
    <p>Hello {name},</p>
    <p>You requested to change your email address to: <strong>{email}</strong></p>
    <p>Click the button below to verify this email address:</p>
    <div style="margin: 30px 0;">
        <a href="{verification_link}" 
           style="background-color: #8B4513; color: white; padding: 12px 30px; 
                  text-decoration: none; border-radius: 4px; display: inline-block;">
            Verify Email
        </a>
    </div>
    <p style="color: #6D4C41; font-size: 14px;">This link will expire in 24 hours.</p>
</body>
</html>
"""
    return (text, html)


def _render_meeting_notification_template(recipient: Dict, meeting: Dict, lab_name: str, server_url: str, **kwargs) -> tuple:
    """Render meeting notification template"""
    text = f"""
Hello,

A new meeting has been scheduled:

Title: {meeting['title']}
Time: {meeting['meeting_time']}
Organizer: {meeting.get('created_by_name', 'Unknown')}

{meeting.get('description', '')}

View meeting details and RSVP:
{server_url}/meetings/{meeting['id']}

Best regards,
{lab_name}
"""
    
    html = f"""
<html>
<body style="font-family: 'Nunito', Arial, sans-serif; color: #3E2723;">
    <h2 style="color: #8B4513;">New Meeting Scheduled</h2>
    <p>Hello {recipient['name']},</p>
    <p>A new meeting has been scheduled:</p>
    <div style="background-color: #FFF8DC; padding: 15px; border-radius: 4px; margin: 20px 0;">
        <p><strong>Title:</strong> {meeting['title']}</p>
        <p><strong>Time:</strong> {meeting['meeting_time']}</p>
        <p><strong>Organizer:</strong> {meeting.get('created_by_name', 'Unknown')}</p>
        {f'<p><strong>Description:</strong> {meeting.get("description", "")}</p>' if meeting.get('description') else ''}
    </div>
    <p>
        <a href="{server_url}/meetings/{meeting['id']}" 
           style="background-color: #8B4513; color: white; padding: 12px 30px; 
                  text-decoration: none; border-radius: 4px; display: inline-block;">
            View Meeting & RSVP
        </a>
    </p>
    <p style="color: #6D4C41; font-size: 12px; margin-top: 30px;">
        {lab_name}
    </p>
</body>
</html>
"""
    return (text, html)


def _render_meeting_update_template(recipient: Dict, meeting: Dict, lab_name: str, server_url: str, **kwargs) -> tuple:
    """Render meeting update notification template"""
    text = f"""
Hello {recipient['name']},

The meeting "{meeting['title']}" has been updated.

New Time: {meeting['meeting_time']}
Organizer: {meeting.get('created_by_name', 'Unknown')}

View updated meeting:
{server_url}/meetings/{meeting['id']}

Best regards,
{lab_name}
"""
    
    html = f"""
<html>
<body style="font-family: 'Nunito', Arial, sans-serif; color: #3E2723;">
    <h2 style="color: #8B4513;">Meeting Time Changed</h2>
    <p>Hello {recipient['name']},</p>
    <p>The meeting <strong>"{meeting['title']}"</strong> has been updated.</p>
    <div style="background-color: #FFF8DC; padding: 15px; border-radius: 4px; margin: 20px 0;">
        <p><strong>New Time:</strong> {meeting['meeting_time']}</p>
        <p><strong>Organizer:</strong> {meeting.get('created_by_name', 'Unknown')}</p>
    </div>
    <p>
        <a href="{server_url}/meetings/{meeting['id']}" 
           style="background-color: #8B4513; color: white; padding: 12px 30px; 
                  text-decoration: none; border-radius: 4px; display: inline-block;">
            View Updated Meeting
        </a>
    </p>
    <p style="color: #6D4C41; font-size: 12px; margin-top: 30px;">
        {lab_name}
    </p>
</body>
</html>
"""
    return (text, html)


def _render_content_notification_template(recipient: Dict, meeting: Dict, content: Dict, lab_name: str, server_url: str, **kwargs) -> tuple:
    """Render content notification template"""
    text = f"""
Hello {recipient['name']},

New content has been uploaded to meeting "{meeting['title']}":

Content: {content['title']}
Uploaded by: {content.get('uploaded_by_name', 'Unknown')}

View and download:
{server_url}/meetings/{meeting['id']}

Best regards,
{lab_name}
"""
    
    html = f"""
<html>
<body style="font-family: 'Nunito', Arial, sans-serif; color: #3E2723;">
    <h2 style="color: #8B4513;">New Meeting Content</h2>
    <p>Hello {recipient['name']},</p>
    <p>New content has been uploaded to meeting <strong>"{meeting['title']}"</strong>:</p>
    <div style="background-color: #FFF8DC; padding: 15px; border-radius: 4px; margin: 20px 0;">
        <p><strong>Content:</strong> {content['title']}</p>
        <p><strong>Uploaded by:</strong> {content.get('uploaded_by_name', 'Unknown')}</p>
        {f'<p><strong>Description:</strong> {content.get("description", "")}</p>' if content.get('description') else ''}
    </div>
    <p>
        <a href="{server_url}/meetings/{meeting['id']}" 
           style="background-color: #8B4513; color: white; padding: 12px 30px; 
                  text-decoration: none; border-radius: 4px; display: inline-block;">
            View & Download
        </a>
    </p>
    <p style="color: #6D4C41; font-size: 12px; margin-top: 30px;">
        {lab_name}
    </p>
</body>
</html>
"""
    return (text, html)


# Public API functions with retry mechanism

@retry_on_failure(max_attempts=3, delay=1)
def send_activation_email(email: str, name: str, activation_link: str) -> bool:
    """Send account activation email with retry"""
    text, html = _render_email_template('activation', name=name, activation_link=activation_link)
    subject = f'{get_lab_name()} - Activate Your Account'
    return _send_email(email, subject, text, html)


@retry_on_failure(max_attempts=3, delay=1)
def send_password_reset_email(email: str, name: str, reset_link: str) -> bool:
    """Send password reset email with retry"""
    text, html = _render_email_template('password_reset', name=name, reset_link=reset_link)
    subject = f'{get_lab_name()} - Password Reset Request'
    return _send_email(email, subject, text, html)


@retry_on_failure(max_attempts=3, delay=1)
def send_email_verification(email: str, name: str, verification_link: str) -> bool:
    """Send email verification email with retry"""
    text, html = _render_email_template('email_verification', name=name, email=email, verification_link=verification_link)
    subject = f'{get_lab_name()} - Verify Email Change'
    return _send_email(email, subject, text, html)


@retry_on_failure(max_attempts=2, delay=2)
def send_meeting_notification(recipient: Dict, meeting: Dict) -> bool:
    """Send meeting notification email with retry"""
    if not recipient.get('email_notifications', True):
        return True  # Skip if notifications disabled
    
    text, html = _render_email_template('meeting_notification', recipient=recipient, meeting=meeting)
    subject = f'New Meeting: {meeting["title"]}'
    return _send_email(recipient['email'], subject, text, html)


@retry_on_failure(max_attempts=2, delay=2)
def send_meeting_update_notification(recipient: Dict, meeting: Dict) -> bool:
    """Send meeting update notification email with retry"""
    if not recipient.get('email_notifications', True):
        return True  # Skip if notifications disabled
    
    text, html = _render_email_template('meeting_update', recipient=recipient, meeting=meeting)
    subject = f'Meeting Updated: {meeting["title"]}'
    return _send_email(recipient['email'], subject, text, html)


@retry_on_failure(max_attempts=2, delay=2)
def send_content_notification(recipient: Dict, meeting: Dict, content: Dict) -> bool:
    """Send content notification email with retry"""
    if not recipient.get('email_notifications', True):
        return True  # Skip if notifications disabled
    
    text, html = _render_email_template('content_notification', recipient=recipient, meeting=meeting, content=content)
    subject = f'New Content: {content["title"]}'
    return _send_email(recipient['email'], subject, text, html)


@retry_on_failure(max_attempts=2, delay=2)
def send_meeting_bulk_notification(creator: Dict, recipients: List[Dict], meeting: Dict) -> bool:
    """Send meeting notification email to creator (TO) and members (CC)"""
    cc_emails = [r['email'] for r in recipients if r.get('email_notifications', True) and r['id'] != creator['id']]
    
    text, html = _render_email_template('meeting_notification', recipient=creator, meeting=meeting)
    subject = f'Meeting: {meeting["title"]}'
    
    return _send_email(creator['email'], subject, text, html, cc_emails=cc_emails)


@retry_on_failure(max_attempts=2, delay=2)
def send_meeting_update_bulk_notification(creator: Dict, recipients: List[Dict], meeting: Dict) -> bool:
    """Send meeting update notification to creator (TO) and members (CC)"""
    cc_emails = [r['email'] for r in recipients if r.get('email_notifications', True) and r['id'] != creator['id']]
    
    text, html = _render_email_template('meeting_update', recipient=creator, meeting=meeting)
    subject = f'Meeting Updated: {meeting["title"]}'
    
    return _send_email(creator['email'], subject, text, html, cc_emails=cc_emails)


@retry_on_failure(max_attempts=2, delay=2)
def send_content_bulk_notification(uploader: Dict, recipients: List[Dict], meeting: Dict, content: Dict) -> bool:
    """Send content notification to uploader (TO) and members (CC)"""
    cc_emails = [r['email'] for r in recipients if r.get('email_notifications', True) and r['id'] != uploader['id']]
    
    text, html = _render_email_template('content_notification', recipient=uploader, meeting=meeting, content=content)
    subject = f'New Content: {content["title"]}'
    
    return _send_email(uploader['email'], subject, text, html, cc_emails=cc_emails)
