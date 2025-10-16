#!/usr/bin/env python3
"""
Database initialization script
"""
import sys
import os
from dotenv import load_dotenv

# Add project root and src to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'src'))

def main():
    """Initialize database tables"""
    # Load environment-specific configuration
    env = os.getenv('ENVIRONMENT', 'development')
    
    if env == 'production':
        load_dotenv(os.path.join(project_root, '.env.prod'))
        print("Initializing production database...")
    else:
        load_dotenv(os.path.join(project_root, '.env.dev'))
        print("Initializing development database...")
    
    try:
        from database.connection import create_tables
        print(f"Creating database tables for {env} environment...")
        create_tables()
        print(f"Database tables created successfully for {env}!")
    except Exception as e:
        print(f"Error creating tables: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
