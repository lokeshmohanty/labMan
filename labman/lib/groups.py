from labman.lib.data import get_db, query_db, execute_db
from labman.lib.helpers import get_lab_name

def create_group(name, description, parent_id=None, lead_id=None):
    """Create a new research group and add creator as member"""
    try:
        cursor = execute_db(
            'INSERT INTO research_groups (name, description, parent_id, lead_id) VALUES (?, ?, ?, ?)',
            (name, description, parent_id, lead_id)
        )
        group_id = cursor.lastrowid
        
        # Creator automatically joins the group
        if lead_id:
            add_user_to_group(lead_id, group_id)
            
        # Log action
        from flask import session
        from labman.lib.audit import log_action
        log_action(session.get('user_id'), "created group", f"Name: {name}")
        
        return True
    except Exception as e:
        print(f"Error creating group: {e}")
        return False

def get_all_groups():
    """Get all research groups"""
    groups = query_db('''
        SELECT g.*, pg.name as parent_name, u.name as lead_name
        FROM research_groups g
        LEFT JOIN research_groups pg ON g.parent_id = pg.id
        LEFT JOIN users u ON g.lead_id = u.id
        ORDER BY g.name
    ''')
    return [dict(group) for group in groups]

def get_all_groups_with_counts():
    """Get all research groups with member counts"""
    groups = query_db('''
        SELECT g.*, pg.name as parent_name, u.name as lead_name,
               COUNT(DISTINCT ug.user_id) as member_count
        FROM research_groups g
        LEFT JOIN research_groups pg ON g.parent_id = pg.id
        LEFT JOIN user_groups ug ON g.id = ug.group_id
        LEFT JOIN users u ON g.lead_id = u.id
        GROUP BY g.id
        ORDER BY g.name
    ''')
    return [dict(group) for group in groups]

def get_group_by_id(group_id):
    """Get group by ID"""
    group = query_db('''
        SELECT g.*, pg.name as parent_name, u.name as lead_name, u.email as lead_email
        FROM research_groups g
        LEFT JOIN research_groups pg ON g.parent_id = pg.id
        LEFT JOIN users u ON g.lead_id = u.id
        WHERE g.id = ?
    ''', [group_id], one=True)
    return dict(group) if group else None

def get_group_by_name(name):
    """Get group by name"""
    group = query_db('SELECT * FROM research_groups WHERE name = ?', [name], one=True)
    return dict(group) if group else None

def update_group(group_id, name, description, parent_id=None, lead_id=None):
    """Update group information"""
    try:
        # Don't allow renaming default Lab group
        group = get_group_by_id(group_id)
        if not group:
            print(f"Group {group_id} not found")
            return False
            
        lab_name = get_lab_name()
        if group['name'] == lab_name and name != lab_name:
            print(f"Cannot rename default '{lab_name}' group")
            return False
        
        execute_db(
            'UPDATE research_groups SET name = ?, description = ?, parent_id = ?, lead_id = ? WHERE id = ?',
            (name, description, parent_id, lead_id, group_id)
        )
        
        # Log action
        from flask import session
        from labman.lib.audit import log_action
        log_action(session.get('user_id'), "updated group", f"Name: {name}")
        
        return True
    except Exception as e:
        print(f"Error updating group: {e}")
        return False

def delete_group(group_id):
    """Delete a research group"""
    try:
        # Don't allow deleting the default Lab group
        group = get_group_by_id(group_id)
        if not group:
            print(f"Group {group_id} not found")
            return False
            
        lab_name = get_lab_name()
        if group['name'] == lab_name:
            print(f"Cannot delete default '{lab_name}' group")
            return False
        
        execute_db('DELETE FROM user_groups WHERE group_id = ?', (group_id,))
        execute_db('DELETE FROM research_groups WHERE id = ?', (group_id,))
        
        # Log action
        from flask import session
        from labman.lib.audit import log_action
        log_action(session.get('user_id'), "deleted group", f"Name: {group['name']}")
        
        return True
    except Exception as e:
        print(f"Error deleting group: {e}")
        return False

def add_user_to_group(user_id, group_id):
    """Add a user to a research group"""
    try:
        execute_db(
            'INSERT OR IGNORE INTO user_groups (user_id, group_id) VALUES (?, ?)',
            (user_id, group_id)
        )
        return True
    except Exception as e:
        print(f"Error adding user to group: {e}")
        return False

def remove_user_from_group(user_id, group_id):
    """Remove a user from a research group"""
    try:
        # Don't allow removing from default Lab group
        group = get_group_by_id(group_id)
        if not group:
            print(f"Group {group_id} not found")
            return False
            
        lab_name = get_lab_name()
        if group['name'] == lab_name:
            print(f"Cannot remove user from default '{lab_name}' group")
            return False
        
        execute_db(
            'DELETE FROM user_groups WHERE user_id = ? AND group_id = ?',
            (user_id, group_id)
        )
        return True
    except Exception as e:
        print(f"Error removing user from group: {e}")
        return False

def get_user_groups(user_id):
    """Get all groups a user belongs to"""
    groups = query_db('''
        SELECT g.*, ug.joined_at
        FROM research_groups g
        INNER JOIN user_groups ug ON g.id = ug.group_id
        WHERE ug.user_id = ?
        ORDER BY g.name
    ''', [user_id])
    return [dict(group) for group in groups]

def get_group_members(group_id):
    """Get all members of a research group"""
    members = query_db('''
        SELECT u.id, u.name, u.email, u.is_admin, ug.joined_at
        FROM users u
        INNER JOIN user_groups ug ON u.id = ug.user_id
        WHERE ug.group_id = ?
        ORDER BY u.name
    ''', [group_id])
    return [dict(member) for member in members]

def get_subgroups(parent_id):
    """Get all subgroups of a parent group"""
    subgroups = query_db(
        'SELECT * FROM research_groups WHERE parent_id = ? ORDER BY name',
        [parent_id]
    )
    return [dict(group) for group in subgroups]

def get_group_hierarchy(group_id):
    """Get the full hierarchy path for a group"""
    hierarchy = []
    current_group = get_group_by_id(group_id)
    
    while current_group:
        hierarchy.insert(0, current_group)
        if current_group['parent_id']:
            current_group = get_group_by_id(current_group['parent_id'])
        else:
            break
    
    return hierarchy

def get_research_tree():
    """Get hierarchy of groups with members"""
    groups = get_all_groups()
    
    # Get all members for all groups
    all_members = query_db('''
        SELECT ug.group_id, u.id, u.name, u.email, u.is_admin, ug.joined_at
        FROM users u
        INNER JOIN user_groups ug ON u.id = ug.user_id
        ORDER BY u.name
    ''')
    
    members_by_group = {}
    for m in all_members:
        gid = m['group_id']
        if gid not in members_by_group:
            members_by_group[gid] = []
        members_by_group[gid].append({
            'id': m['id'], 'name': m['name'], 'email': m['email'], 
            'is_admin': m['is_admin'], 'joined_at': m['joined_at']
        })
        
    # Build tree
    groups_map = {}
    for g in groups:
        g_dict = dict(g)
        g_dict['members'] = members_by_group.get(g['id'], [])
        g_dict['subgroups'] = []
        groups_map[g['id']] = g_dict
        
    roots = []
    for g_id, g in groups_map.items():
        if g['parent_id'] and g['parent_id'] in groups_map:
            groups_map[g['parent_id']]['subgroups'].append(g)
        else:
            roots.append(g)
            
    return roots
