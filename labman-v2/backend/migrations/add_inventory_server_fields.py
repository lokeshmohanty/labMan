"""Add missing fields to inventory and servers

This migration adds:
- status and notes columns to inventory table
- name, specs, status, and notes columns to servers table
"""

import sqlite3
import os

# Get database path
db_path = os.path.join(os.path.dirname(__file__), '..', 'labman.db')

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    # Add columns to inventory table
    print("Adding columns to inventory table...")
    try:
        cursor.execute("ALTER TABLE inventory ADD COLUMN status TEXT DEFAULT 'available'")
        print("  - Added status column")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("  - status column already exists")
        else:
            raise
    
    try:
        cursor.execute("ALTER TABLE inventory ADD COLUMN notes TEXT")
        print("  - Added notes column")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("  - notes column already exists")
        else:
            raise
    
    # Add columns to servers table
    print("\nAdding columns to servers table...")
    try:
        cursor.execute("ALTER TABLE servers ADD COLUMN name TEXT")
        print("  - Added name column")
        # Update existing rows to have a name based on hostname
        cursor.execute("UPDATE servers SET name = hostname WHERE name IS NULL")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("  - name column already exists")
        else:
            raise
    
    try:
        cursor.execute("ALTER TABLE servers ADD COLUMN specs TEXT")
        print("  - Added specs column")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("  - specs column already exists")
        else:
            raise
    
    try:
        cursor.execute("ALTER TABLE servers ADD COLUMN status TEXT DEFAULT 'active'")
        print("  - Added status column")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("  - status column already exists")
        else:
            raise
    
    try:
        cursor.execute("ALTER TABLE servers ADD COLUMN notes TEXT")
        print("  - Added notes column")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("  - notes column already exists")
        else:
            raise
    
    conn.commit()
    print("\n✅ Migration completed successfully!")
    
except Exception as e:
    conn.rollback()
    print(f"\n❌ Migration failed: {e}")
    raise
finally:
    conn.close()
