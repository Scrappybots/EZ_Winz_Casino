#!/usr/bin/env python3
"""
Wait for PostgreSQL database to be ready before starting the application
"""
import os
import sys
import time
import psycopg2
from urllib.parse import urlparse

def wait_for_db(database_url, max_retries=30, retry_interval=2):
    """
    Wait for database to be ready
    
    Args:
        database_url: PostgreSQL connection URL
        max_retries: Maximum number of connection attempts
        retry_interval: Seconds to wait between retries
    """
    parsed = urlparse(database_url)
    
    connection_params = {
        'host': parsed.hostname,
        'port': parsed.port or 5432,
        'user': parsed.username,
        'password': parsed.password,
        'database': parsed.path[1:] if parsed.path else 'postgres'
    }
    
    print(f"🔍 Waiting for PostgreSQL at {parsed.hostname}:{connection_params['port']}...")
    
    for attempt in range(1, max_retries + 1):
        try:
            conn = psycopg2.connect(**connection_params)
            conn.close()
            print(f"✅ PostgreSQL is ready! (attempt {attempt}/{max_retries})")
            return True
        except psycopg2.OperationalError as e:
            if attempt == max_retries:
                print(f"❌ Failed to connect to PostgreSQL after {max_retries} attempts")
                print(f"   Error: {e}")
                return False
            print(f"⏳ PostgreSQL not ready yet (attempt {attempt}/{max_retries}), retrying in {retry_interval}s...")
            time.sleep(retry_interval)
    
    return False


if __name__ == '__main__':
    database_url = os.environ.get('DATABASE_URL')
    
    if not database_url:
        print("❌ DATABASE_URL environment variable not set")
        sys.exit(1)
    
    if not database_url.startswith('postgresql://'):
        print("⚠️  DATABASE_URL is not a PostgreSQL URL, skipping wait")
        sys.exit(0)
    
    if wait_for_db(database_url):
        sys.exit(0)
    else:
        sys.exit(1)
