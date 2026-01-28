import os
import sys
from datetime import datetime, timedelta
from labman.server import app
from labman.lib.users import create_user, update_user_password, get_user_by_email, get_all_users, delete_user
from labman.lib.groups import create_group, add_user_to_group, get_group_by_name, get_all_groups, delete_group
from labman.lib.meetings import create_meeting, get_all_meetings, delete_meeting
from labman.lib.content import upload_content, get_content, delete_content
from labman.lib.inventory import add_inventory_item, get_all_inventory, delete_inventory_item
from labman.lib.servers import add_server, get_all_servers, delete_server

# ... MockFile class ...

def populate():
    # ... existing populate code ...
    print("\nData population complete!")

def clear():
    print("Clearing test data...")
    with app.app_context():
        # 1. Clear Users
        print("\nRemoving test users...")
        test_emails = [
            "alice@example.com", "bob@example.com", 
            "charlie@example.com", "dave@example.com"
        ]
        
        for email in test_emails:
            user = get_user_by_email(email)
            if user:
                # Delete user content first (best effort)
                user_content = get_content(user_id=user['id'])
                for c in user_content:
                    delete_content(c['id'])
                
                # Delete user meetings created by them
                all_meetings = get_all_meetings()
                for m in all_meetings:
                    if m['created_by'] == user['id']:
                        delete_meeting(m['id'])

                if delete_user(user['id']):
                    print(f"  Deleted user: {user['name']}")
                else:
                    print(f"  Failed to delete user: {user['name']}")
            else:
                print(f"  User not found: {email}")

        # 2. Clear Groups
        print("\nRemoving test groups...")
        test_groups = [
            "Quantum Computing", "Bio-Informatics", "Robotics"
        ]
        
        for name in test_groups:
            group = get_group_by_name(name)
            if group:
                if delete_group(group['id']):
                    print(f"  Deleted group: {name}")
                else:
                    print(f"  Failed to delete group: {name}")
            else:
                print(f"  Group not found: {name}")

        # 3. Clear Inventory
        print("\nRemoving test inventory...")
        test_inventory = ["Oscilloscope", "Microscope", "Beakers", "Soldering Iron"]
        
        # Iterate all inventory to find matches by name
        all_inv = get_all_inventory()
        for item in all_inv:
            if item['name'] in test_inventory:
                delete_inventory_item(item['id'])
                print(f"  Deleted inventory: {item['name']}")

        # 4. Clear Servers
        print("\nRemoving test servers...")
        test_servers = ["gpu-cluster-01", "storage-nas"]
        
        all_servers = get_all_servers()
        for srv in all_servers:
            if srv['hostname'] in test_servers:
                delete_server(srv['id'])
                print(f"  Deleted server: {srv['hostname']}")

    print("\nTest data cleared!")

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'clear':
        clear()
    else:
        populate()
