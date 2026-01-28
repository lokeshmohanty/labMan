from werkzeug.security import generate_password_hash
from labman.lib.data import get_db, query_db, execute_db
from labman.lib.helpers import get_lab_group, get_server_url
from datetime import datetime, timedelta
import secrets

def create_user(name, email, password, is_admin=False):
    """Create a new user and send activation email"""
    try:
        # Create user without password (will be set on activation)
        cursor = execute_db(
            'INSERT INTO users (name, email, password_hash, is_admin) VALUES (?, ?, ?, ?)',
            (name, email, None, is_admin)
        )
        user_id = cursor.lastrowid
        
        # Add user to default Lab group
        lab_group = get_lab_group()
        if lab_group:
            execute_db('INSERT INTO user_groups (user_id, group_id) VALUES (?, ?)',
                      (user_id, lab_group['id']))
        
        # Send activation email using centralized service
        from labman.lib.email_service import send_activation_email
        token = create_password_reset_token(user_id)
        activation_link = f"{get_server_url()}/activate/{token}"
        send_activation_email(email, name, activation_link)
        
        return True
    except Exception as e:
        print(f"Error creating user: {e}")
        return False

def send_activation_email(email, name, user_id):
    """Send account activation email"""
    token = create_password_reset_token(user_id)
    host = os.getenv('HOST_IP', 'localhost')
    port = os.getenv('SERVER_PORT', '9000')
    activation_link = f"http://{host}:{port}/activate/{token}"
    
    try:
        lab_name = os.getenv('LAB_NAME', 'Lab Manager')
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f'{lab_name} - Activate Your Account'
        msg['From'] = SENDER_EMAIL
        msg['To'] = email
        
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
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #3E2723;">
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
        
        part1 = MIMEText(text, 'plain')
        part2 = MIMEText(html, 'html')
        msg.attach(part1)
        msg.attach(part2)
        
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(msg)
        
        return True
    except Exception as e:
        print(f"Error sending activation email: {e}")
        return False

def send_meeting_notification(meeting, recipients):
    """Send email notification about new meeting"""
    for recipient in recipients:
        if not recipient.get('email_notifications', True):
            continue
            
        try:
            lab_name = os.getenv('LAB_NAME', 'Lab Manager')
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f'New Meeting: {meeting["title"]}'
            msg['From'] = SENDER_EMAIL
            msg['To'] = recipient['email']
            
            text = f"""
Hello {recipient['name']},

A new meeting has been scheduled:

Title: {meeting['title']}
Time: {meeting['meeting_time']}
Organizer: {meeting.get('created_by_name', 'Unknown')}

{meeting.get('description', '')}

View meeting details and RSVP:
http://{os.getenv('HOST_IP', 'localhost')}:{os.getenv('SERVER_PORT', '9000')}/meetings/{meeting['id']}

Best regards,
{lab_name}
"""
            
            html = f"""
<html>
<body style="font-family: Arial, sans-serif; color: #3E2723;">
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
        <a href="http://{os.getenv('HOST_IP', 'localhost')}:{os.getenv('SERVER_PORT', '9000')}/meetings/{meeting['id']}" 
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
            
            part1 = MIMEText(text, 'plain')
            part2 = MIMEText(html, 'html')
            msg.attach(part1)
            msg.attach(part2)
            
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls()
                server.login(SMTP_USERNAME, SMTP_PASSWORD)
                server.send_message(msg)
        except Exception as e:
            print(f"Error sending meeting notification to {recipient['email']}: {e}")

def send_meeting_update_notification(meeting, recipients):
    """Send email notification about meeting time/date change"""
    for recipient in recipients:
        if not recipient.get('email_notifications', True):
            continue
            
        try:
            lab_name = os.getenv('LAB_NAME', 'Lab Manager')
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f'Meeting Updated: {meeting["title"]}'
            msg['From'] = SENDER_EMAIL
            msg['To'] = recipient['email']
            
            html = f"""
<html>
<body style="font-family: Arial, sans-serif; color: #3E2723;">
    <h2 style="color: #8B4513;">Meeting Time Changed</h2>
    <p>Hello {recipient['name']},</p>
    <p>The meeting <strong>"{meeting['title']}"</strong> has been updated.</p>
    <div style="background-color: #FFF8DC; padding: 15px; border-radius: 4px; margin: 20px 0;">
        <p><strong>New Time:</strong> {meeting['meeting_time']}</p>
        <p><strong>Organizer:</strong> {meeting.get('created_by_name', 'Unknown')}</p>
    </div>
    <p>
        <a href="http://{os.getenv('HOST_IP', 'localhost')}:{os.getenv('SERVER_PORT', '9000')}/meetings/{meeting['id']}" 
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
            msg.attach(MIMEText(html, 'html'))
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls()
                server.login(SMTP_USERNAME, SMTP_PASSWORD)
                server.send_message(msg)
        except Exception as e:
            print(f"Error sending meeting update notification to {recipient['email']}: {e}")

def send_content_notification(meeting, content, recipients):
    """Send notification about new meeting content"""
    for recipient in recipients:
        if not recipient.get('email_notifications', True):
            continue
            
        try:
            lab_name = os.getenv('LAB_NAME', 'Lab Manager')
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f'New Content: {content["title"]}'
            msg['From'] = SENDER_EMAIL
            msg['To'] = recipient['email']
            
            text = f"""
Hello {recipient['name']},

New content has been uploaded to meeting "{meeting['title']}":

Content: {content['title']}
Uploaded by: {content.get('uploaded_by_name', 'Unknown')}

View and download:
http://{os.getenv('HOST_IP', 'localhost')}:{os.getenv('SERVER_PORT', '9000')}/meetings/{meeting['id']}

Best regards,
{lab_name}
"""
            
            html = f"""
<html>
<body style="font-family: Arial, sans-serif; color: #3E2723;">
    <h2 style="color: #8B4513;">New Meeting Content</h2>
    <p>Hello {recipient['name']},</p>
    <p>New content has been uploaded to meeting <strong>"{meeting['title']}"</strong>:</p>
    <div style="background-color: #FFF8DC; padding: 15px; border-radius: 4px; margin: 20px 0;">
        <p><strong>Content:</strong> {content['title']}</p>
        <p><strong>Uploaded by:</strong> {content.get('uploaded_by_name', 'Unknown')}</p>
        {f'<p><strong>Description:</strong> {content.get("description", "")}</p>' if content.get('description') else ''}
    </div>
    <p>
        <a href="http://{os.getenv('HOST_IP', 'localhost')}:{os.getenv('SERVER_PORT', '9000')}/meetings/{meeting['id']}" 
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
            
            part1 = MIMEText(text, 'plain')
            part2 = MIMEText(html, 'html')
            msg.attach(part1)
            msg.attach(part2)
            
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls()
                server.login(SMTP_USERNAME, SMTP_PASSWORD)
                server.send_message(msg)
        except Exception as e:
            print(f"Error sending content notification to {recipient['email']}: {e}")

def get_all_users():
    """Get all users"""
    users = query_db('SELECT id, name, email, is_admin, email_notifications, created_at, password_hash FROM users ORDER BY name')
    return [dict(user) for user in users]

def get_user_by_id(user_id):
    """Get user by ID"""
    user = query_db('SELECT id, name, email, is_admin, email_notifications, created_at FROM users WHERE id = ?', 
                    [user_id], one=True)
    return dict(user) if user else None

def get_user_by_email(email):
    """Get user by email"""
    user = query_db('SELECT id, name, email, is_admin, email_notifications, created_at FROM users WHERE email = ?', 
                    [email], one=True)
    return dict(user) if user else None

def update_user(user_id, name, email, is_admin=False):
    """Update user information"""
    try:
        execute_db(
            'UPDATE users SET name = ?, email = ?, is_admin = ? WHERE id = ?',
            (name, email, is_admin, user_id)
        )
        return True
    except Exception as e:
        print(f"Error updating user: {e}")
        return False

def update_user_password(user_id, new_password):
    """Update user password"""
    try:
        password_hash = generate_password_hash(new_password)
        execute_db('UPDATE users SET password_hash = ? WHERE id = ?', (password_hash, user_id))
        return True
    except Exception as e:
        print(f"Error updating password: {e}")
        return False

def update_user_notifications(user_id, enabled):
    """Update user notification preferences"""
    try:
        execute_db('UPDATE users SET email_notifications = ? WHERE id = ?', (enabled, user_id))
        return True
    except Exception as e:
        print(f"Error updating notifications: {e}")
        return False

def update_user_profile(user_id, name, new_email):
    """Update user profile (name and optionally email)"""
    try:
        current_user = get_user_by_id(user_id)
        if not current_user:
            return False
        
        # If email is changing, send verification
        if new_email and new_email != current_user['email']:
            # Create verification token
            token = create_password_reset_token(user_id)
            host = os.getenv('HOST_IP', 'localhost')
            port = os.getenv('SERVER_PORT', '9000')
            verification_link = f"http://{host}:{port}/verify-email/{token}?email={new_email}"
            
            # Send verification email to NEW email
            send_email_verification(new_email, name, verification_link)
            
            # Only update name for now, email will be updated after verification
            execute_db('UPDATE users SET name = ? WHERE id = ?', (name, user_id))
            return 'verification_sent'
        else:
            # Only updating name
            execute_db('UPDATE users SET name = ? WHERE id = ?', (name, user_id))
            return True
    except Exception as e:
        print(f"Error updating profile: {e}")
        return False

def verify_email_change(user_id, new_email):
    """Verify and update email after user confirms"""
    try:
        execute_db('UPDATE users SET email = ? WHERE id = ?', (new_email, user_id))
        return True
    except Exception as e:
        print(f"Error verifying email: {e}")
        return False

def send_email_verification(email, name, verification_link):
    """Send email verification link"""
    try:
        lab_name = os.getenv('LAB_NAME', 'Lab Manager')
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f'{lab_name} - Verify Email Change'
        msg['From'] = SENDER_EMAIL
        msg['To'] = email
        
        html = f"""
<html>
<body style="font-family: Arial, sans-serif; color: #3E2723;">
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
        msg.attach(MIMEText(html, 'html'))
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(msg)
        return True
    except Exception as e:
        print(f"Error sending verification email: {e}")
        return False

def delete_user(user_id):
    """Delete a user"""
    try:
        execute_db('DELETE FROM user_groups WHERE user_id = ?', (user_id,))
        execute_db('DELETE FROM users WHERE id = ?', (user_id,))
        return True
    except Exception as e:
        print(f"Error deleting user: {e}")
        return False

def create_password_reset_token(user_id):
    """Create a password reset token for a user"""
    token = secrets.token_urlsafe(32)
    expires_at = datetime.now() + timedelta(hours=24)
    
    try:
        execute_db(
            'INSERT INTO password_reset_tokens (user_id, token, expires_at) VALUES (?, ?, ?)',
            (user_id, token, expires_at)
        )
        return token
    except Exception as e:
        print(f"Error creating reset token: {e}")
        return None

def verify_reset_token(token):
    """Verify a password reset token and return user_id if valid"""
    try:
        result = query_db(
            '''SELECT user_id FROM password_reset_tokens 
               WHERE token = ? AND used = 0 AND expires_at > datetime('now')''',
            [token], one=True
        )
        return result['user_id'] if result else None
    except Exception as e:
        print(f"Error verifying token: {e}")
        return None

def get_latest_activation_token(user_id):
    """Get the latest unused activation token for a user"""
    try:
        token = query_db(
            '''SELECT * FROM password_reset_tokens 
               WHERE user_id = ? AND used = 0 
               ORDER BY created_at DESC LIMIT 1''',
            [user_id], one=True
        )
        return dict(token) if token else None
    except Exception as e:
        print(f"Error getting latest token: {e}")
        return None

def resend_activation_email(user_id):
    """Resend activation email to a user"""
    try:
        user = get_user_by_id(user_id)
        if not user:
            return False
            
        # Delete existing unused tokens
        execute_db('DELETE FROM password_reset_tokens WHERE user_id = ? AND used = 0', (user_id,))
        
        # Send new activation email
        return send_activation_email(user['email'], user['name'], user_id)
    except Exception as e:
        print(f"Error resending activation email: {e}")
        return False

def send_password_reset_email(email, name, reset_link):
    """Send password reset email to user"""
    try:
        lab_name = os.getenv('LAB_NAME', 'Lab Manager')
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f'{lab_name} - Password Reset Request'
        msg['From'] = SENDER_EMAIL
        msg['To'] = email
        
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
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #3E2723;">
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
        
        part1 = MIMEText(text, 'plain')
        part2 = MIMEText(html, 'html')
        msg.attach(part1)
        msg.attach(part2)
        
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(msg)
        
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False
