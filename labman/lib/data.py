import sqlite3
from flask import g
import os
from dotenv import load_dotenv

load_dotenv()



# Ensure data directory exists in the project root
# Use current working directory as the base (where labman is run from)
db_dir = os.path.join(os.getcwd(), 'data')
os.makedirs(db_dir, exist_ok=True)

db_filename = os.getenv('LAB_NAME', 'Demo Lab').lower().replace(" ", "_") + '.db'
DATABASE = os.path.join(db_dir, db_filename)

def get_db():
    """Get database connection"""
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

def close_db(e=None):
    """Close database connection"""
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    """Initialize database with schema"""
    db = get_db()
    
    # Users table
    db.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT,
            is_admin BOOLEAN DEFAULT 0,
            email_notifications BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Research groups table
    db.execute('''
        CREATE TABLE IF NOT EXISTS research_groups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            description TEXT,
            parent_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (parent_id) REFERENCES research_groups(id)
        )
    ''')
    
    # User-Group membership table
    db.execute('''
        CREATE TABLE IF NOT EXISTS user_groups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            group_id INTEGER NOT NULL,
            joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (group_id) REFERENCES research_groups(id) ON DELETE CASCADE,
            UNIQUE(user_id, group_id)
        )
    ''')
    
    # Meetings table
    db.execute('''
        CREATE TABLE IF NOT EXISTS meetings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            meeting_time TIMESTAMP NOT NULL,
            created_by INTEGER NOT NULL,
            group_id INTEGER,
            tags TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (created_by) REFERENCES users(id),
            FOREIGN KEY (group_id) REFERENCES research_groups(id)
        )
    ''')
    
    # Meeting responses table
    db.execute('''
        CREATE TABLE IF NOT EXISTS meeting_responses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            meeting_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            response TEXT CHECK(response IN ('join', 'wont_join')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (meeting_id) REFERENCES meetings(id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            UNIQUE(meeting_id, user_id)
        )
    ''')
    
    # Content table
    db.execute('''
        CREATE TABLE IF NOT EXISTS content (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            filename TEXT NOT NULL,
            file_path TEXT NOT NULL,
            file_size INTEGER,
            uploaded_by INTEGER NOT NULL,
            group_id INTEGER,
            meeting_id INTEGER,
            research_plan_id INTEGER,  -- Linked to research_plans
            access_level TEXT DEFAULT 'group',
            share_link TEXT UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (uploaded_by) REFERENCES users(id),
            FOREIGN KEY (group_id) REFERENCES research_groups(id),
            FOREIGN KEY (meeting_id) REFERENCES meetings(id),
            FOREIGN KEY (research_plan_id) REFERENCES research_plans(user_id)
        )
    ''')
    
    # Inventory table
    db.execute('''
        CREATE TABLE IF NOT EXISTS inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            quantity INTEGER DEFAULT 0,
            location TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Servers table
    db.execute('''
        CREATE TABLE IF NOT EXISTS servers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            hostname TEXT NOT NULL,
            ip_address TEXT NOT NULL,
            admin_name TEXT,
            location TEXT,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Research Plans table
    db.execute('''
        CREATE TABLE IF NOT EXISTS research_plans (
            user_id INTEGER PRIMARY KEY,
            problem_statement TEXT,
            research_progress TEXT,  -- New field
            github_link TEXT,
            manuscript_link TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            start_date DATE,
            end_date DATE,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')
    
    # Research Tasks table
    db.execute('''
        CREATE TABLE IF NOT EXISTS research_tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            task_name TEXT NOT NULL,
            due_date DATE,
            start_date DATE,
            previous_due_date DATE,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')
    
    # Password reset tokens table
    db.execute('''
        CREATE TABLE IF NOT EXISTS password_reset_tokens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            token TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP NOT NULL,
            used BOOLEAN DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')
    
    # Email failures table for tracking failed email attempts
    db.execute('''
        CREATE TABLE IF NOT EXISTS email_failures (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email_type TEXT NOT NULL,
            recipient TEXT NOT NULL,
            error_message TEXT,
            payload TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            retry_count INTEGER DEFAULT 0,
            last_retry_at TIMESTAMP
        )
    ''')
    
    # Create default Lab group if it doesn't exist
    lab_name = os.getenv('LAB_NAME', 'Lab Manager')
    existing_group = db.execute('SELECT id FROM research_groups WHERE name = ?', (lab_name,)).fetchone()
    if not existing_group:
        db.execute('INSERT INTO research_groups (name, description) VALUES (?, ?)',
                  (lab_name, f'Default {lab_name} group for all members'))
    
    # Create default admin user if no users exist
    existing_users = db.execute('SELECT COUNT(*) as count FROM users').fetchone()
    if existing_users['count'] == 0:
        from werkzeug.security import generate_password_hash
        password_hash = generate_password_hash('admin123')
        admin_email = os.getenv('SMTP_USERNAME', 'admin@example.com')
        cursor = db.execute('INSERT INTO users (name, email, password_hash, is_admin) VALUES (?, ?, ?, ?)',
                           ('Admin User', admin_email, password_hash, 1))
        user_id = cursor.lastrowid
        
        # Add admin to default Lab group
        lab_group = db.execute('SELECT id FROM research_groups WHERE name = ?', (lab_name,)).fetchone()
        if lab_group:
            db.execute('INSERT INTO user_groups (user_id, group_id) VALUES (?, ?)',
                      (user_id, lab_group['id']))
    
    db.commit()

def query_db(query, args=(), one=False):
    """Execute a query and return results"""
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

def execute_db(query, args=()):
    """Execute a query that modifies data"""
    db = get_db()
    cursor = db.execute(query, args)
    db.commit()
    return cursor
