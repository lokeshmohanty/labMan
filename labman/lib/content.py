import os
import secrets
from werkzeug.utils import secure_filename
from labman.lib.data import get_db, query_db, execute_db
from labman.lib.auth import check_user_group_access
from labman.lib.helpers import get_lab_members
from labman.lib.email_queue import email_queue

def allowed_file(filename):
    """Check if file extension is allowed - allowing all for now"""
    return True

def generate_share_link():
    """Generate a unique share link"""
    return secrets.token_urlsafe(32)

def upload_content(file, title, description, uploaded_by, group_id=None, meeting_id=None, research_plan_id=None, access_level='group', upload_folder='uploads'):
    """Upload a new content file"""
    try:
        if not file or not allowed_file(file.filename):
            print("Invalid file or file type")
            return False
        
        filename = secure_filename(file.filename)
        
        save_path = upload_folder
        if group_id:
            save_path = os.path.join(save_path, f"group_{group_id}")
        if meeting_id:
            save_path = os.path.join(save_path, f"meeting_{meeting_id}")
        if research_plan_id:
            save_path = os.path.join(save_path, f"research_{research_plan_id}")
        
        os.makedirs(save_path, exist_ok=True)
        
        base_filename = filename
        counter = 1
        while os.path.exists(os.path.join(save_path, filename)):
            name, ext = os.path.splitext(base_filename)
            filename = f"{name}_{counter}{ext}"
            counter += 1
        
        file_path = os.path.join(save_path, filename)
        file.save(file_path)
        
        file_size = os.path.getsize(file_path)
        
        share_link = generate_share_link() if access_level == 'link' else None
        
        cursor = execute_db(
            '''INSERT INTO content (title, description, filename, file_path, file_size, 
               uploaded_by, group_id, meeting_id, research_plan_id, access_level, share_link) 
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (title, description, filename, file_path, file_size, uploaded_by, 
             group_id, meeting_id, research_plan_id, access_level, share_link)
        )
        content_id = cursor.lastrowid
        
        # Send notification if uploaded to a meeting
        if meeting_id:
            from labman.lib.meetings import get_meeting_by_id
            from labman.lib.email_service import send_content_notification
            
            meeting = get_meeting_by_id(meeting_id)
            content_item = get_content_by_id(content_id)
            
            if meeting and content_item:
                members = get_lab_members()
                if members:
                    # Queue content notifications in background
                    for member in members:
                        email_queue.enqueue(send_content_notification, recipient=member, meeting=meeting, content=content_item)
        
        return True
    except Exception as e:
        print(f"Error uploading content: {e}")
        return False

def get_content(user_id=None, group_id=None, meeting_id=None, research_plan_id=None):
    """Get content with optional filters"""
    query = '''
        SELECT c.*, u.name as uploaded_by_name, g.name as group_name, m.title as meeting_title
        FROM content c
        LEFT JOIN users u ON c.uploaded_by = u.id
        LEFT JOIN research_groups g ON c.group_id = g.id
        LEFT JOIN meetings m ON c.meeting_id = m.id
        WHERE 1=1
    '''
    params = []
    
    if user_id:
        query += ' AND c.uploaded_by = ?'
        params.append(user_id)
    
    if group_id:
        query += ' AND c.group_id = ?'
        params.append(group_id)
    
    if meeting_id:
        query += ' AND c.meeting_id = ?'
        params.append(meeting_id)
        
    if research_plan_id:
        query += ' AND c.research_plan_id = ?'
        params.append(research_plan_id)
    
    query += ' ORDER BY c.created_at DESC'
    
    content = query_db(query, params)
    return [dict(item) for item in content]

def get_content_by_id(content_id):
    """Get content by ID"""
    content = query_db('''
        SELECT c.*, u.name as uploaded_by_name, g.name as group_name, m.title as meeting_title
        FROM content c
        LEFT JOIN users u ON c.uploaded_by = u.id
        LEFT JOIN research_groups g ON c.group_id = g.id
        LEFT JOIN meetings m ON c.meeting_id = m.id
        WHERE c.id = ?
    ''', [content_id], one=True)
    return dict(content) if content else None

def get_content_by_share_link(share_link):
    """Get content by share link"""
    content = query_db('''
        SELECT c.*, u.name as uploaded_by_name
        FROM content c
        LEFT JOIN users u ON c.uploaded_by = u.id
        WHERE c.share_link = ? AND c.access_level = 'link'
    ''', [share_link], one=True)
    return dict(content) if content else None

def check_content_access(content_id, user_id=None):
    """Check if user has access to content"""
    content = get_content_by_id(content_id)
    
    if not content:
        return False
    
    # Public content (link access)
    if content['access_level'] == 'link':
        return True
    
    # Allow access to all registered users
    if user_id:
        return True

    return False

def update_content(content_id, title, description, group_id=None, meeting_id=None, research_plan_id=None, access_level='group'):
    """Update content metadata"""
    try:
        # If changing to link access, generate share link
        share_link = None
        if access_level == 'link':
            existing = get_content_by_id(content_id)
            if existing:
                share_link = existing.get('share_link') or generate_share_link()
            else:
                share_link = generate_share_link()
        
        execute_db(
            'UPDATE content SET title = ?, description = ?, group_id = ?, meeting_id = ?, research_plan_id = ?, access_level = ?, share_link = ? WHERE id = ?',
            (title, description, group_id, meeting_id, research_plan_id, access_level, share_link, content_id)
        )
        return True
    except Exception as e:
        print(f"Error updating content: {e}")
        return False

def delete_content(content_id):
    """Delete content and its file"""
    try:
        content = get_content_by_id(content_id)
        if content:
            # Delete the file
            if os.path.exists(content['file_path']):
                os.remove(content['file_path'])
            
            # Delete from database
            execute_db('DELETE FROM content WHERE id = ?', (content_id,))
            return True
        return False
    except Exception as e:
        print(f"Error deleting content: {e}")
        return False

def search_content(search_term, user_id=None):
    """Search content by title, description, or filename"""
    search_pattern = f"%{search_term}%"
    query = '''
        SELECT c.*, u.name as uploaded_by_name, g.name as group_name, m.title as meeting_title
        FROM content c
        LEFT JOIN users u ON c.uploaded_by = u.id
        LEFT JOIN research_groups g ON c.group_id = g.id
        LEFT JOIN meetings m ON c.meeting_id = m.id
        WHERE c.title LIKE ? OR c.description LIKE ? OR c.filename LIKE ?
    '''
    params = [search_pattern, search_pattern, search_pattern]
    
    if user_id:
        query += ' AND c.uploaded_by = ?'
        params.append(user_id)
    
    query += ' ORDER BY c.created_at DESC'
    
    content = query_db(query, params)
    return [dict(item) for item in content]

def get_content_by_group(group_id):
    """Get content for specific group"""
    content = query_db('''
        SELECT c.*, u.name as uploaded_by_name, g.name as group_name, m.title as meeting_title
        FROM content c
        LEFT JOIN users u ON c.uploaded_by = u.id
        LEFT JOIN research_groups g ON c.group_id = g.id
        LEFT JOIN meetings m ON c.meeting_id = m.id
        WHERE c.group_id = ?
        ORDER BY c.created_at DESC
    ''', [group_id])
    return [dict(item) for item in content]
