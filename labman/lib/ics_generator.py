def generate_ics_file(meeting):
    """Generate ICS file content for a meeting"""
    from datetime import timedelta
    import os
    from zoneinfo import ZoneInfo
    from datetime import datetime
    import uuid
    
    try:
        # Get timezone from environment variable
        timezone_str = os.getenv('TIMEZONE', 'Asia/Kolkata')
        
        # Parse meeting time - handle multiple formats
        meeting_time_str = meeting['meeting_time']
        dt = None
        
        # Try different datetime formats
        formats_to_try = [
            '%Y-%m-%dT%H:%M',           # ISO format without seconds
            '%Y-%m-%d %H:%M:%S',        # Standard format with seconds
            '%Y-%m-%dT%H:%M:%S',        # ISO format with seconds
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
        
        # Format for ICS (YYYYMMDDTHHMMSSZ)
        start_str = dt_utc.strftime('%Y%m%dT%H%M%SZ')
        end_str = end_dt_utc.strftime('%Y%m%dT%H%M%SZ')
        timestamp = datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
        
        # Generate unique ID
        uid = f"{meeting['id']}-{uuid.uuid4()}@labman"
        
        # Escape special characters in ICS format
        def ics_escape(text):
            if not text:
                return ''
            return text.replace('\\', '\\\\').replace(',', '\\,').replace(';', '\\;').replace('\n', '\\n')
        
        title = ics_escape(meeting['title'])
        description = ics_escape(meeting['description'] or '')
        
        # Create ICS content
        ics_content = f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//LabMan//Meeting Calendar//EN
CALSCALE:GREGORIAN
METHOD:PUBLISH
BEGIN:VEVENT
UID:{uid}
DTSTAMP:{timestamp}
DTSTART:{start_str}
DTEND:{end_str}
SUMMARY:{title}
DESCRIPTION:{description}
STATUS:CONFIRMED
SEQUENCE:0
END:VEVENT
END:VCALENDAR"""
        
        return ics_content
    except Exception as e:
        print(f"Error generating ICS file: {e}")
        import traceback
        traceback.print_exc()
        return None
