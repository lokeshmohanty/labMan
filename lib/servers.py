from lib.data import get_db, query_db, execute_db

def add_server(hostname, ip_address, admin_name, location, description):
    """Add a new server"""
    try:
        execute_db(
            'INSERT INTO servers (hostname, ip_address, admin_name, location, description) VALUES (?, ?, ?, ?, ?)',
            (hostname, ip_address, admin_name, location, description)
        )
        return True
    except Exception as e:
        print(f"Error adding server: {e}")
        return False

def get_all_servers():
    """Get all servers"""
    servers = query_db('SELECT * FROM servers ORDER BY hostname')
    return [dict(server) for server in servers]

def get_server_by_id(server_id):
    """Get server by ID"""
    server = query_db('SELECT * FROM servers WHERE id = ?', [server_id], one=True)
    return dict(server) if server else None

def update_server(server_id, hostname, ip_address, admin_name, location, description):
    """Update server information"""
    try:
        execute_db(
            '''UPDATE servers 
               SET hostname = ?, ip_address = ?, admin_name = ?, location = ?, description = ?, updated_at = CURRENT_TIMESTAMP 
               WHERE id = ?''',
            (hostname, ip_address, admin_name, location, description, server_id)
        )
        return True
    except Exception as e:
        print(f"Error updating server: {e}")
        return False

def delete_server(server_id):
    """Delete a server"""
    try:
        execute_db('DELETE FROM servers WHERE id = ?', (server_id,))
        return True
    except Exception as e:
        print(f"Error deleting server: {e}")
        return False

def search_servers(search_term):
    """Search servers by hostname, IP, or admin"""
    search_pattern = f"%{search_term}%"
    servers = query_db(
        '''SELECT * FROM servers 
           WHERE hostname LIKE ? OR ip_address LIKE ? OR admin_name LIKE ? 
           ORDER BY hostname''',
        [search_pattern, search_pattern, search_pattern]
    )
    return [dict(server) for server in servers]
