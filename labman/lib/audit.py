from labman.lib.data import execute_db, query_db

def log_action(user_id, action, details=None):
    """Log an action to the audit_logs table"""
    try:
        execute_db(
            'INSERT INTO audit_logs (user_id, action, details) VALUES (?, ?, ?)',
            (user_id, action, details)
        )
        return True
    except Exception as e:
        print(f"Error logging action: {e}")
        return False

def get_audit_logs(limit=100, user_id=None, action=None):
    """Get recent audit logs with user names and optional filters"""
    try:
        query = '''
            SELECT a.*, u.name as user_name
            FROM audit_logs a
            LEFT JOIN users u ON a.user_id = u.id
            WHERE 1=1
        '''
        params = []
        
        if user_id:
            query += ' AND a.user_id = ?'
            params.append(user_id)
            
        if action:
            query += ' AND a.action = ?'
            params.append(action)
            
        query += ' ORDER BY a.created_at DESC LIMIT ?'
        params.append(limit)
        
        logs = query_db(query, params)
        return [dict(log) for log in logs]
    except Exception as e:
        print(f"Error fetching audit logs: {e}")
        return []
