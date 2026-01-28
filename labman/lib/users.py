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
            # Generate verification link
            verification_link = f"{get_server_url()}/verify-email/{token}?email={new_email}"
            
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
    """Send email verification link using centralized service"""
    from labman.lib.email_service import send_email_verification as send_email
    return send_email(email, name, verification_link)

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
        
        # Create new activation token
        token = create_password_reset_token(user_id)
        if not token:
            return False
            
        # Generate activation link
        activation_link = f"{get_server_url()}/activate/{token}"
        
        # Send activation email using centralized service
        from labman.lib.email_service import send_activation_email as send_email
        return send_email(user['email'], user['name'], activation_link)
    except Exception as e:
        print(f"Error resending activation email: {e}")
        return False

def send_password_reset_email(email, name, reset_link):
    """Send password reset email using centralized service"""
    from labman.lib.email_service import send_password_reset_email as send_email
    return send_email(email, name, reset_link)
