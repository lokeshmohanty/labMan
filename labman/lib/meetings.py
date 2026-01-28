from labman.lib.data import get_db, query_db, execute_db
from datetime import datetime
import calendar

def create_meeting(title, description, meeting_time, created_by, group_id=None, tags=None):
    """Create a new meeting"""
    try:
        tags_str = ','.join(tags) if tags else None
        cursor = execute_db(
            'INSERT INTO meetings (title, description, meeting_time, created_by, group_id, tags) VALUES (?, ?, ?, ?, ?, ?)',
            (title, description, meeting_time, created_by, group_id, tags_str)
        )
        meeting_id = cursor.lastrowid
        
        # Send notifications to Airex Lab group members
        from labman.lib.users import send_meeting_notification
        from labman.lib.groups import get_group_members
        
        airex_group = query_db('SELECT id FROM research_groups WHERE name = ?', ['Airex Lab'], one=True)
        if airex_group:
            members = get_group_members(airex_group['id'])
            meeting = get_meeting_by_id(meeting_id)
            send_meeting_notification(meeting, members)
        
        return True
    except Exception as e:
        print(f"Error creating meeting: {e}")
        return False

def get_all_meetings(limit=None):
    """Get all meetings"""
    query = '''
        SELECT m.*, u.name as created_by_name, g.name as group_name
        FROM meetings m
        LEFT JOIN users u ON m.created_by = u.id
        LEFT JOIN research_groups g ON m.group_id = g.id
        ORDER BY m.meeting_time DESC
    '''
    
    if limit:
        query += f' LIMIT {limit}'
    
    meetings = query_db(query)
    return [dict(meeting) for meeting in meetings]

def get_meetings_this_week():
    """Get meetings for current week"""
    meetings = query_db('''
        SELECT m.*, u.name as created_by_name, g.name as group_name
        FROM meetings m
        LEFT JOIN users u ON m.created_by = u.id
        LEFT JOIN research_groups g ON m.group_id = g.id
        WHERE DATE(m.meeting_time) >= DATE('now', 'weekday 0', '-6 days')
        AND DATE(m.meeting_time) <= DATE('now', 'weekday 0')
        ORDER BY m.meeting_time ASC
    ''')
    return [dict(meeting) for meeting in meetings]

def get_meetings_by_month(year, month):
    """Get meetings for specific month"""
    meetings = query_db('''
        SELECT m.*, u.name as created_by_name, g.name as group_name
        FROM meetings m
        LEFT JOIN users u ON m.created_by = u.id
        LEFT JOIN research_groups g ON m.group_id = g.id
        WHERE strftime('%Y', m.meeting_time) = ?
        AND strftime('%m', m.meeting_time) = ?
        ORDER BY m.meeting_time ASC
    ''', [str(year), f"{month:02d}"])
    return [dict(meeting) for meeting in meetings]

def get_meetings_by_tags(tags):
    """Get meetings filtered by tags"""
    if not tags:
        return get_all_meetings()
    
    # Use exact matching strategy for comma-separated values
    # We pad the stored tags with commas: ',tag1,tag2,' and search for ',tag,'
    tag_conditions = ' OR '.join(["',' || tags || ',' LIKE ?" for _ in tags])
    
    # Pad the search terms with commas
    tag_params = [f'%,{tag.strip()},%' for tag in tags]
    
    meetings = query_db(f'''
        SELECT m.*, u.name as created_by_name, g.name as group_name
        FROM meetings m
        LEFT JOIN users u ON m.created_by = u.id
        LEFT JOIN research_groups g ON m.group_id = g.id
        WHERE ({tag_conditions})
        ORDER BY m.meeting_time DESC
    ''', tag_params)
    return [dict(meeting) for meeting in meetings]

def get_meeting_by_id(meeting_id):
    """Get meeting by ID"""
    meeting = query_db('''
        SELECT m.*, u.name as created_by_name, g.name as group_name
        FROM meetings m
        LEFT JOIN users u ON m.created_by = u.id
        LEFT JOIN research_groups g ON m.group_id = g.id
        WHERE m.id = ?
    ''', [meeting_id], one=True)
    return dict(meeting) if meeting else None

def get_meetings_by_group(group_id):
    """Get all meetings for a specific group"""
    meetings = query_db('''
        SELECT m.*, u.name as created_by_name, g.name as group_name
        FROM meetings m
        LEFT JOIN users u ON m.created_by = u.id
        LEFT JOIN research_groups g ON m.group_id = g.id
        WHERE m.group_id = ?
        ORDER BY m.meeting_time DESC
    ''', [group_id])
    return [dict(meeting) for meeting in meetings]

def update_meeting(meeting_id, title, description, meeting_time, group_id=None, tags=None, send_notification=False):
    """Update meeting information"""
    try:
        tags_str = ','.join(tags) if tags else None
        execute_db(
            'UPDATE meetings SET title = ?, description = ?, meeting_time = ?, group_id = ?, tags = ? WHERE id = ?',
            (title, description, meeting_time, group_id, tags_str, meeting_id)
        )
        
        # Send notification if time changed
        if send_notification:
            from labman.lib.users import send_meeting_update_notification
            from labman.lib.groups import get_group_members
            
            meeting = get_meeting_by_id(meeting_id)
            airex_group = query_db('SELECT id FROM research_groups WHERE name = ?', ['Airex Lab'], one=True)
            if airex_group:
                members = get_group_members(airex_group['id'])
                send_meeting_update_notification(meeting, members)
        
        return True
    except Exception as e:
        print(f"Error updating meeting: {e}")
        return False

def get_all_tags():
    """Get all unique tags used in meetings"""
    tags_data = query_db('SELECT tags FROM meetings WHERE tags IS NOT NULL AND tags != ""')
    unique_tags = set()
    
    for row in tags_data:
        if row['tags']:
            for tag in row['tags'].split(','):
                unique_tags.add(tag.strip())
                
    return sorted(list(unique_tags))

def format_meeting_datetime(dt_str):
    """Format datetime string to '22 Jan, 2026 (Thu) @ 10:00 AM'"""
    try:
        dt = datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S')
        day = dt.day
        month = calendar.month_abbr[dt.month]
        year = dt.year
        weekday = calendar.day_abbr[dt.weekday()]
        time = dt.strftime('%I:%M %p')
        return f"{day} {month}, {year} ({weekday}) @ {time}"
    except:
        try:
            dt = datetime.fromisoformat(dt_str.replace('T', ' '))
            day = dt.day
            month = calendar.month_abbr[dt.month]
            year = dt.year
            weekday = calendar.day_abbr[dt.weekday()]
            time = dt.strftime('%I:%M %p')
            return f"{day} {month}, {year} ({weekday}) @ {time}"
        except:
            return dt_str

def delete_meeting(meeting_id):
    """Delete a meeting"""
    try:
        execute_db('DELETE FROM meetings WHERE id = ?', (meeting_id,))
        return True
    except Exception as e:
        print(f"Error deleting meeting: {e}")
        return False

def record_meeting_response(meeting_id, user_id, response):
    """Record user's response to meeting"""
    try:
        execute_db('''
            INSERT OR REPLACE INTO meeting_responses (meeting_id, user_id, response)
            VALUES (?, ?, ?)
        ''', (meeting_id, user_id, response))
        return True
    except Exception as e:
        print(f"Error recording response: {e}")
        return False

def get_meeting_responses(meeting_id):
    """Get all responses for a meeting"""
    responses = query_db('''
        SELECT mr.*, u.name as user_name, u.email
        FROM meeting_responses mr
        JOIN users u ON mr.user_id = u.id
        WHERE mr.meeting_id = ?
        ORDER BY mr.response, u.name
    ''', [meeting_id])
    return [dict(r) for r in responses]
