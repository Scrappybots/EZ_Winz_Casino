"""
Database initialization script for NeoBank & Chrome Slots
Run this script to set up the database with initial data
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))

from backend.app import app, init_database

if __name__ == '__main__':
    print("🚀 Initializing NeoBank database...")
    init_database()
    print("✅ Database initialization complete!")
    print("\n📋 Default admin credentials:")
    print("   Username: admin")
    print("   Password: neotropolis2025")
    print("\n👥 Predefined user accounts:")
    print("   Username: Ralph")
    print("   Password: Rodney32")
    print("   Username: Strixen")
    print("   Password: Forty2seven")
    print("   Username: Chaos")
    print("   Password: Thelovelydog")
    print("\n⚠️  IMPORTANT: Change the admin password immediately in production!")
