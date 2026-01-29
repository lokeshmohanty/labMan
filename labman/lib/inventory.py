from labman.lib.data import get_db, query_db, execute_db
from datetime import datetime

def add_inventory_item(name, description, quantity, location):
    """Add a new inventory item"""
    try:
        execute_db(
            'INSERT INTO inventory (name, description, quantity, location) VALUES (?, ?, ?, ?)',
            (name, description, quantity, location)
        )
        # Log action
        from flask import session
        from labman.lib.audit import log_action
        log_action(session.get('user_id'), "added inventory item", f"Name: {name}")
        return True
    except Exception as e:
        print(f"Error adding inventory item: {e}")
        return False

def get_all_inventory():
    """Get all inventory items"""
    items = query_db('SELECT * FROM inventory ORDER BY name')
    return [dict(item) for item in items]

def get_inventory_by_id(item_id):
    """Get inventory item by ID"""
    item = query_db('SELECT * FROM inventory WHERE id = ?', [item_id], one=True)
    return dict(item) if item else None

def update_inventory_item(item_id, name, description, quantity, location):
    """Update inventory item"""
    try:
        execute_db(
            '''UPDATE inventory 
               SET name = ?, description = ?, quantity = ?, location = ?, updated_at = CURRENT_TIMESTAMP 
               WHERE id = ?''',
            (name, description, quantity, location, item_id)
        )
        # Log action
        from flask import session
        from labman.lib.audit import log_action
        log_action(session.get('user_id'), "updated inventory item", f"ItemID: {item_id}, Name: {name}")
        return True
    except Exception as e:
        print(f"Error updating inventory item: {e}")
        return False

def update_inventory_quantity(item_id, quantity_change):
    """Update inventory quantity (positive to add, negative to remove)"""
    try:
        execute_db(
            '''UPDATE inventory 
               SET quantity = quantity + ?, updated_at = CURRENT_TIMESTAMP 
               WHERE id = ?''',
            (quantity_change, item_id)
        )
        return True
    except Exception as e:
        print(f"Error updating inventory quantity: {e}")
        return False

def delete_inventory_item(item_id):
    """Delete an inventory item"""
    try:
        item = get_inventory_by_id(item_id)
        execute_db('DELETE FROM inventory WHERE id = ?', (item_id,))
        # Log action
        from flask import session
        from labman.lib.audit import log_action
        if item:
            log_action(session.get('user_id'), "deleted inventory item", f"Name: {item['name']}")
        return True
    except Exception as e:
        print(f"Error deleting inventory item: {e}")
        return False

def search_inventory(search_term):
    """Search inventory by name, description, or location"""
    search_pattern = f"%{search_term}%"
    items = query_db(
        '''SELECT * FROM inventory 
           WHERE name LIKE ? OR description LIKE ? OR location LIKE ? 
           ORDER BY name''',
        [search_pattern, search_pattern, search_pattern]
    )
    return [dict(item) for item in items]

def get_low_stock_items(threshold=5):
    """Get items with quantity below threshold"""
    items = query_db(
        'SELECT * FROM inventory WHERE quantity <= ? ORDER BY quantity ASC',
        [threshold]
    )
    return [dict(item) for item in items]

def get_inventory_by_location(location):
    """Get all inventory items at a specific location"""
    items = query_db(
        'SELECT * FROM inventory WHERE location = ? ORDER BY name',
        [location]
    )
    return [dict(item) for item in items]

def get_all_locations():
    """Get all unique locations"""
    locations = query_db('SELECT DISTINCT location FROM inventory WHERE location IS NOT NULL ORDER BY location')
    return [loc['location'] for loc in locations]
