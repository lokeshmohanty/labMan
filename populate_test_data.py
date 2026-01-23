import os
import sys
from datetime import datetime, timedelta
from app import app
from lib.users import create_user, update_user_password, get_user_by_email, get_all_users
from lib.groups import create_group, add_user_to_group, get_group_by_name, get_all_groups
from lib.meetings import create_meeting
from lib.content import upload_content
from lib.inventory import add_inventory_item, get_all_inventory
from lib.servers import add_server

# Mock File class for content upload
class MockFile:
    def __init__(self, filename, content=b"dummy content"):
        self.filename = filename
        self.content = content
    
    def save(self, path):
        with open(path, 'wb') as f:
            f.write(self.content)

def populate():
    print("Starting data population...")
    
    with app.app_context():
        # 1. Create Users
        print("\nCreating users...")
        users_data = [
            ("Alice Researcher", "alice@example.com", "password123", False),
            ("Bob Scientist", "bob@example.com", "password123", False),
            ("Charlie Admin", "charlie@example.com", "admin123", True),
            ("Dave Student", "dave@example.com", "password123", False),
        ]
        
        for name, email, password, is_admin in users_data:
            if not get_user_by_email(email):
                if create_user(name, email, password, is_admin):
                    print(f"  Created user: {name}")
                    # Manually set password since create_user only sets up activation
                    user = get_user_by_email(email)
                    update_user_password(user['id'], password)
                else:
                    print(f"  Failed to create user: {name}")
            else:
                print(f"  User {name} already exists.")

        # Refresh user list
        users = {u['email']: u for u in get_all_users()}
        alice = users.get('alice@example.com')
        bob = users.get('bob@example.com')
        charlie = users.get('charlie@example.com')
        
        # 2. Create Groups
        print("\nCreating groups...")
        groups_data = [
            ("Quantum Computing", "Research into quantum bits and gates", None),
            ("Bio-Informatics", "Analysis of biological data", None),
            ("Robotics", "Autonomous systems and control", None),
        ]
        
        for name, desc, parent_id in groups_data:
            if not get_group_by_name(name):
                if create_group(name, desc, parent_id):
                    print(f"  Created group: {name}")
                else:
                    print(f"  Failed to create group: {name}")
            else:
                print(f"  Group {name} already exists.")
                
        # Get groups
        groups = {g['name']: g for g in get_all_groups()}
        quantum_grp = groups.get('Quantum Computing')
        bio_grp = groups.get('Bio-Informatics')
        
        # 3. Add members to groups
        print("\nAdding members to groups...")
        if alice and quantum_grp:
            add_user_to_group(alice['id'], quantum_grp['id'])
            print(f"  Added {alice['name']} to {quantum_grp['name']}")
        
        if bob and bio_grp:
            add_user_to_group(bob['id'], bio_grp['id'])
            print(f"  Added {bob['name']} to {bio_grp['name']}")
            
        if charlie and quantum_grp:
            add_user_to_group(charlie['id'], quantum_grp['id'])
            print(f"  Added {charlie['name']} to {quantum_grp['name']}")

        # 4. Create Meetings
        print("\nCreating meetings...")
        now = datetime.now()
        meetings_data = [
            ("Weekly Quantum Sync", "Status updates for quantum project", (now + timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S'), charlie, quantum_grp, ["weekly", "sync"]),
            ("Bio Lab Safety Training", "Mandatory safety training", (now + timedelta(days=2)).strftime('%Y-%m-%d %H:%M:%S'), bob, bio_grp, ["safety", "training"]),
            ("Project Kickoff", "New robotics project kickoff", (now + timedelta(days=5)).strftime('%Y-%m-%d %H:%M:%S'), alice, None, ["kickoff"]),
        ]
        
        for title, desc, time, creator, group, tags in meetings_data:
            if creator:
                create_meeting(title, desc, time, creator['id'], group['id'] if group else None, tags)
                print(f"  Created meeting: {title}")

        # 5. Create Content
        print("\nCreating content...")
        mock_file1 = MockFile("research_notes.txt", b"These are some important notes.")
        mock_file2 = MockFile("lab_results.csv", b"sample,value\nA,10\nB,20")
        
        if alice:
            upload_content(mock_file1, "Quantum Research Notes", "Initial thoughts", alice['id'], quantum_grp['id'] if quantum_grp else None, None, 'group', app.config['UPLOAD_FOLDER'])
            print("  Uploaded research_notes.txt")
            
        if bob:
            upload_content(mock_file2, "Beta Test Results", "Preliminary results", bob['id'], bio_grp['id'] if bio_grp else None, None, 'group', app.config['UPLOAD_FOLDER'])
            print("  Uploaded lab_results.csv")

        # 6. Create Inventory & Servers
        print("\nCreating inventory...")
        inventory_data = [
            ("Oscilloscope", "Digital storage oscilloscope", 2, "Shelf A"),
            ("Microscope", "Electron microscope", 1, "Lab 2"),
            ("Beakers", "500ml glass beakers", 50, "Cabinet B"),
            ("Soldering Iron", "Variable temperature", 5, "Workbench 1"),
        ]
        
        for name, desc, qty, loc in inventory_data:
            # Check if exists (simple check by name not implemented in lib, so just add)
            add_inventory_item(name, desc, qty, loc)
            print(f"  Added inventory: {name}")

        print("\nCreating servers...")
        servers_data = [
            ("gpu-cluster-01", "192.168.1.10", "Charlie", "Server Room", "Main GPU cluster for training"),
            ("storage-nas", "192.168.1.20", "Alice", "Server Room", "Shared storage"),
        ]
        
        for host, ip, admin, loc, desc in servers_data:
            add_server(host, ip, admin, loc, desc)
            print(f"  Added server: {host}")

    print("\nData population complete!")

if __name__ == '__main__':
    populate()
