#!/usr/bin/env python3
"""Script to create missing database tables"""
import sys
sys.path.insert(0, '/home/lokesh/Projects/labman/labman-v2/backend')

from app.database import Base, engine
from app.models import GroupProject, GroupTask

# Create only the missing tables
print("Creating missing database tables...")
Base.metadata.create_all(bind=engine, tables=[GroupProject.__table__, GroupTask.__table__])
print("✓ group_projects table created")
print("✓ group_tasks table created")
print("\nDatabase tables created successfully!")
