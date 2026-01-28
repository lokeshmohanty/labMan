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
from labman.lib.research import add_research_task, update_research_problem
from labman.lib.helpers import get_lab_group

class MockFile:
    def __init__(self, filename, content=b"mock content"):
        self.filename = filename
        self.content = content
    def save(self, path):
        with open(path, 'wb') as f:
            f.write(self.content)

def populate():
    print("Populating test data...")
    with app.app_context():
        # Get default lab group
        lab_group = get_lab_group()
        lab_group_id = lab_group['id'] if lab_group else None
        
        # 1. Create Users
        print("\nCreating users...")
        users_data = [
            ("Alice Johnson", "alice@example.com", "password123", True),
            ("Bob Smith", "bob@example.com", "password123", False),
            ("Charlie Brown", "charlie@example.com", "password123", False),
            ("Dave Wilson", "dave@example.com", "password123", False)
        ]
        
        for name, email, password, is_admin in users_data:
            if not get_user_by_email(email):
                if create_user(name, email, None, is_admin):
                    user = get_user_by_email(email)
                    update_user_password(user['id'], password)
                    print(f"  Created user: {name}")
            else:
                print(f"  User already exists: {name}")

        # 2. Create Groups
        print("\nCreating groups...")
        groups_data = [
            ("Quantum Computing", "Research on quantum algorithms and hardware."),
            ("Bio-Informatics", "Data analysis for biological systems."),
            ("Robotics", "Autonomous systems and robotics hardware.")
        ]
        
        for name, desc in groups_data:
            if not get_group_by_name(name):
                if create_group(name, desc, parent_id=lab_group_id):
                    print(f"  Created group: {name} (Parent: {lab_group_id})")
            else:
                print(f"  Group already exists: {name}")

        # 3. Add Users to Groups
        print("\nAssigning users to groups...")
        alice = get_user_by_email("alice@example.com")
        bob = get_user_by_email("bob@example.com")
        charlie = get_user_by_email("charlie@example.com")
        
        qc_group = get_group_by_name("Quantum Computing")
        bio_group = get_group_by_name("Bio-Informatics")
        rob_group = get_group_by_name("Robotics")

        if alice and qc_group: add_user_to_group(alice['id'], qc_group['id'])
        if bob and qc_group: add_user_to_group(bob['id'], qc_group['id'])
        if bob and bio_group: add_user_to_group(bob['id'], bio_group['id'])
        if charlie and rob_group: add_user_to_group(charlie['id'], rob_group['id'])
        print("  User assignments complete.")

        # 4. Add Inventory
        print("\nAdding inventory...")
        inventory_items = [
            ("Oscilloscope", "Digital storage oscilloscope, 100MHz", 2, "Lab A-101"),
            ("Microscope", "Confocal laser scanning microscope", 1, "Lab B-205"),
            ("Beakers", "500ml Pyrex beakers", 50, "Storage Room"),
            ("Soldering Iron", "Weller soldering station", 5, "Workshop")
        ]
        
        all_inv = get_all_inventory()
        existing_inv = [item['name'] for item in all_inv]
        
        for name, desc, qty, loc in inventory_items:
            if name not in existing_inv:
                if add_inventory_item(name, desc, qty, loc):
                    print(f"  Added inventory: {name}")
            else:
                print(f"  Inventory already exists: {name}")

        # 5. Add Servers
        print("\nAdding servers...")
        servers_data = [
            ("gpu-cluster-01", "192.168.1.50", "Alice Johnson", "Rack 1", "Main compute cluster with 8x A100 GPUs"),
            ("storage-nas", "192.168.1.60", "Bob Smith", "Rack 2", "200TB shared storage")
        ]
        
        all_srv = get_all_servers()
        existing_srv = [srv['hostname'] for srv in all_srv]
        
        for host, ip, admin, loc, desc in servers_data:
            if host not in existing_srv:
                if add_server(host, ip, admin, loc, desc):
                    print(f"  Added server: {host}")
            else:
                print(f"  Server already exists: {host}")

        # 6. Add Meetings
        print("\nCreating meetings...")
        now = datetime.now()
        meetings_data = [
            ("Weekly QC Sync", "Sync on quantum algorithm progress", (now + timedelta(days=1)).strftime('%Y-%m-%d 10:00:00'), alice['id'] if alice else 1, qc_group['id'] if qc_group else None, ["qc", "sync"]),
            ("Robotics Workshop", "Hands-on session with new drones", (now + timedelta(days=3)).strftime('%Y-%m-%d 14:00:00'), charlie['id'] if charlie else 1, rob_group['id'] if rob_group else None, ["robotics", "workshop"]),
            ("Bio-Informatics Seminar", "Guest lecture on genomic pipelines", (now - timedelta(days=2)).strftime('%Y-%m-%d 11:00:00'), bob['id'] if bob else 1, bio_group['id'] if bio_group else None, ["bio", "seminar"])
        ]
        
        for title, desc, m_time, c_by, g_id, tags in meetings_data:
            if create_meeting(title, desc, m_time, c_by, g_id, tags):
                print(f"  Created meeting: {title}")

        # 7. Add Research Plans and Tasks
        print("\nAdding research plans and tasks...")
        if alice:
            update_research_problem(alice['id'], "Optimizing Shor's Algorithm for noisy hardware.", "Completed literature review.")
            add_research_task(alice['id'], "Implement noise model", (now + timedelta(days=7)).strftime('%Y-%m-%d'), "pending")
            add_research_task(alice['id'], "Run simulations on IBM Q", (now + timedelta(days=14)).strftime('%Y-%m-%d'), "pending")
            
            # 8. Add Content
            print("\nUploading content...")
            mock_file = MockFile("research_plan_qc.pdf", b"Optimizing Shor's Algorithm content")
            upload_content(mock_file, "Shors Optimization Plan", "Detailed roadmap for the research project.", alice['id'], research_plan_id=alice['id'])
            
            # Link content to meeting
            meeting = get_all_meetings(limit=1)[0]
            mock_meeting_notes = MockFile("sync_notes_jan_28.txt", b"Notes from today's sync.")
            upload_content(mock_meeting_notes, "Sync Notes", "Action items from the sync.", alice['id'], meeting_id=meeting['id'])
            print("  Created research plan, tasks, and uploaded content.")

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
