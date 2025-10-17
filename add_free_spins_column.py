#!/usr/bin/env python3
"""
Database migration script to add free_spins column to users table
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app import app, db
from models import User

def add_free_spins_column():
    """Add free_spins column to existing users"""
    with app.app_context():
        try:
            # Try to add the column using raw SQL
            from sqlalchemy import text
            
            # Check if column already exists
            result = db.session.execute(text(
                "SELECT column_name FROM information_schema.columns "
                "WHERE table_name='users' AND column_name='free_spins'"
            ))
            
            if result.fetchone() is None:
                print("Adding free_spins column to users table...")
                db.session.execute(text(
                    "ALTER TABLE users ADD COLUMN free_spins INTEGER DEFAULT 0 NOT NULL"
                ))
                db.session.commit()
                print("✅ Successfully added free_spins column!")
            else:
                print("✅ free_spins column already exists!")
                
        except Exception as e:
            print(f"❌ Error: {e}")
            db.session.rollback()
            sys.exit(1)

if __name__ == '__main__':
    add_free_spins_column()
