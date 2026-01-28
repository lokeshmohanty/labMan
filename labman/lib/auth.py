from flask import session, redirect, url_for, flash
from functools import wraps
from werkzeug.security import check_password_hash
from labman.lib.data import get_db, query_db

def login_user(email, password):
    """Authenticate user and return user object if successful"""
    user = query_db('SELECT * FROM users WHERE email = ?', [email], one=True)
    
    if user and check_password_hash(user['password_hash'], password):
        return dict(user)
    return None

def logout_user():
    """Clear user session"""
    session.clear()

def get_current_user():
    """Get currently logged in user"""
    if 'user_id' not in session:
        return None
    
    user = query_db('SELECT id, name, email, is_admin FROM users WHERE id = ?', 
                    [session['user_id']], one=True)
    return dict(user) if user else None

def is_admin():
    """Check if current user is admin"""
    return session.get('is_admin', False)

def require_login(f):
    """Decorator to require login for a route"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page', 'error')
            return redirect(url_for('login'))
        
        # Verify user still exists in database
        user = query_db('SELECT id FROM users WHERE id = ?', [session['user_id']], one=True)
        if not user:
            # User was deleted, clear session
            session.clear()
            flash('Your account no longer exists. Please contact an administrator.', 'error')
            return redirect(url_for('login'))
        
        return f(*args, **kwargs)
    return decorated_function

def require_admin(f):
    """Decorator to require admin access for a route"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page', 'error')
            return redirect(url_for('login'))
        
        # Verify user still exists in database
        user = query_db('SELECT id, is_admin FROM users WHERE id = ?', [session['user_id']], one=True)
        if not user:
            # User was deleted, clear session
            session.clear()
            flash('Your account no longer exists. Please contact an administrator.', 'error')
            return redirect(url_for('login'))
        
        if not user['is_admin']:
            flash('Admin access required', 'error')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

def check_user_group_access(user_id, group_id):
    """Check if user has access to a specific group"""
    if not user_id:
        return False
    
    # Admins have access to all groups
    user = query_db('SELECT is_admin FROM users WHERE id = ?', [user_id], one=True)
    if user and user['is_admin']:
        return True
    
    # Check if user is member of the group
    membership = query_db('SELECT id FROM user_groups WHERE user_id = ? AND group_id = ?',
                         [user_id, group_id], one=True)
    return membership is not None

def check_content_ownership(user_id, content_id):
    """Check if user owns the content"""
    if not user_id:
        return False
    
    content = query_db('SELECT uploaded_by FROM content WHERE id = ?', [content_id], one=True)
    return content and content['uploaded_by'] == user_id
