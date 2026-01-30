from labman.lib.data import get_db, query_db, execute_db
from labman.lib.helpers import get_lab_members
from labman.lib.email_queue import email_queue
from datetime import datetime
import calendar

def create_meeting(title, description, meeting_time, created_by, group_id=None, tags=None, summary=None):
    """Create a new meeting"""
    try:
        tags_str = ','.join(tags) if tags else None
        cursor = execute_db(
            'INSERT INTO meetings (title, description, meeting_time, created_by, group_id, tags, summary) VALUES (?, ?, ?, ?, ?, ?, ?)',
            (title, description, meeting_time, created_by, group_id, tags_str, summary)
        )
        meeting_id = cursor.lastrowid
        
        # Auto-join creator to the meeting
        record_meeting_response(meeting_id, created_by, 'join')
        
        # Send notifications to Group members in background
        from labman.lib.email_service import send_meeting_bulk_notification
        from labman.lib.users import get_user_by_id
        from labman.lib.groups import get_group_members
        from labman.lib.audit import log_action
        
        meeting = get_meeting_by_id(meeting_id)
        
        # If no group specified (should be mandatory now), fallback to lab members
        if group_id:
            members = get_group_members(group_id)
        else:
            members = get_lab_members()
            
        creator = get_user_by_id(created_by)
        
        if meeting and members and creator:
            # Queue bulk notification
            email_queue.enqueue(send_meeting_bulk_notification, creator=creator, recipients=members, meeting=meeting)
        
        # Log action
        log_action(created_by, "created meeting", f"Title: {title}, Group ID: {group_id}")
        
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

def update_meeting(meeting_id, title, description, meeting_time, group_id=None, tags=None, summary=None, send_notification=False):
    """Update meeting information"""
    try:
        tags_str = ','.join(tags) if tags else None
        execute_db(
            'UPDATE meetings SET title = ?, description = ?, meeting_time = ?, group_id = ?, tags = ?, summary = ? WHERE id = ?',
            (title, description, meeting_time, group_id, tags_str, summary, meeting_id)
        )
        
        # Send notification if time changed
        if send_notification:
            from labman.lib.email_service import send_meeting_update_bulk_notification
            from labman.lib.users import get_user_by_id
            from labman.lib.groups import get_group_members
            
            meeting = get_meeting_by_id(meeting_id)
            if not meeting:
                print(f"Meeting {meeting_id} not found for notification")
                return True  # Update succeeded, just skip notification
            
            creator = get_user_by_id(meeting['created_by'])
            
            if group_id:
                members = get_group_members(group_id)
            else:
                members = get_lab_members()
            
            if members and creator:
                # Queue bulk update notification
                email_queue.enqueue(send_meeting_update_bulk_notification, creator=creator, recipients=members, meeting=meeting)
        
        # Log action
        from flask import session
        from labman.lib.audit import log_action
        log_action(session.get('user_id'), "updated meeting", f"Meeting ID: {meeting_id}, Title: {title}")
        
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
    """Format datetime string to '22 Jan, 2026 (Thu) @ 10:00 AM' with timezone support"""
    import os
    from zoneinfo import ZoneInfo
    
    # Get timezone from environment variable, default to Asia/Kolkata
    timezone_str = os.getenv('TIMEZONE', 'Asia/Kolkata')
    
    try:
        # Parse the datetime string - try multiple formats
        dt = None
        formats_to_try = [
            '%Y-%m-%dT%H:%M',           # ISO format without seconds: 2026-01-30T14:52
            '%Y-%m-%d %H:%M:%S',        # Standard format with seconds: 2026-01-30 14:52:00
            '%Y-%m-%dT%H:%M:%S',        # ISO format with seconds: 2026-01-30T14:52:00
        ]
        
        for fmt in formats_to_try:
            try:
                dt = datetime.strptime(dt_str, fmt)
                break
            except ValueError:
                continue
        
        if dt is None:
            # If we can't parse it, return the original string
            return dt_str
        
        # Assume the stored time is in local timezone
        dt_local = dt.replace(tzinfo=ZoneInfo(timezone_str))
        
        day = dt_local.day
        month = calendar.month_abbr[dt_local.month]
        year = dt_local.year
        weekday = calendar.day_abbr[dt_local.weekday()]
        time = dt_local.strftime('%I:%M %p')
        return f"{day} {month}, {year} ({weekday}) @ {time}"
    except Exception as e:
        print(f"Error formatting datetime '{dt_str}': {e}")
        return dt_str


def delete_meeting(meeting_id):
    """Delete a meeting"""
    try:
        meeting = get_meeting_by_id(meeting_id)
        execute_db('DELETE FROM meetings WHERE id = ?', (meeting_id,))
        
        # Log action
        from flask import session
        from labman.lib.audit import log_action
        if meeting:
            log_action(session.get('user_id'), "deleted meeting", f"Title: {meeting.get('title')}")
            
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

def update_meeting_summary(meeting_id, summary):
    """Update only the summary field of a meeting"""
    try:
        execute_db(
            'UPDATE meetings SET summary = ? WHERE id = ?',
            (summary, meeting_id)
        )
        
        # Log action
        from flask import session
        from labman.lib.audit import log_action
        log_action(session.get('user_id'), "updated meeting summary", f"Meeting ID: {meeting_id}")
        
        return True
    except Exception as e:
        print(f"Error updating meeting summary: {e}")
        return False

def generate_calendar_links(meeting):
    """Generate Google and Outlook calendar links for a meeting"""
    from urllib.parse import quote
    from datetime import timedelta
    import os
    from zoneinfo import ZoneInfo
    
    try:
        # Get timezone from environment variable
        timezone_str = os.getenv('TIMEZONE', 'Asia/Kolkata')
        
        # Parse meeting time - handle multiple formats
        meeting_time_str = meeting['meeting_time']
        dt = None
        
        # Try different datetime formats
        formats_to_try = [
            '%Y-%m-%dT%H:%M',           # ISO format without seconds: 2026-01-30T14:52
            '%Y-%m-%d %H:%M:%S',        # Standard format with seconds: 2026-01-30 14:52:00
            '%Y-%m-%dT%H:%M:%S',        # ISO format with seconds: 2026-01-30T14:52:00
        ]
        
        for fmt in formats_to_try:
            try:
                dt = datetime.strptime(meeting_time_str, fmt)
                break
            except ValueError:
                continue
        
        if dt is None:
            raise ValueError(f"Could not parse datetime: {meeting_time_str}")
        
        # Assume the stored time is in local timezone, convert to UTC
        dt_local = dt.replace(tzinfo=ZoneInfo(timezone_str))
        dt_utc = dt_local.astimezone(ZoneInfo('UTC'))
        
        # Assume 1-hour duration
        end_dt_utc = dt_utc + timedelta(hours=1)
        
        # Format for calendar APIs (use UTC times in ISO format)
        start_str = dt_utc.strftime('%Y%m%dT%H%M%SZ')
        end_str = end_dt_utc.strftime('%Y%m%dT%H%M%SZ')
        
        title = quote(meeting['title'])
        description = quote(meeting['description'] or '')
        
        # Google Calendar URL
        google_url = f"https://calendar.google.com/calendar/render?action=TEMPLATE&text={title}&dates={start_str}/{end_str}&details={description}"
        
        # Outlook Calendar URL - use proper ISO format with Z suffix
        outlook_start = dt_utc.strftime('%Y-%m-%dT%H:%M:%SZ')
        outlook_end = end_dt_utc.strftime('%Y-%m-%dT%H:%M:%SZ')
        outlook_url = f"https://outlook.office.com/calendar/0/deeplink/compose?subject={title}&startdt={outlook_start}&enddt={outlook_end}&body={description}&path=/calendar/action/compose&rru=addevent"
        
        return {
            'google': google_url,
            'outlook': outlook_url
        }
    except Exception as e:
        print(f"Error generating calendar links: {e}")
        import traceback
        traceback.print_exc()
        return {
            'google': '#',
            'outlook': '#'
        }



