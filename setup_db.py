import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import os
import sys

def create_database():
    # Common local configurations to try
    configs = [
        {'user': os.environ.get('USER', 'postgres'), 'host': 'localhost', 'port': '5432', 'password': ''},
        {'user': 'postgres', 'host': 'localhost', 'port': '5432', 'password': ''},
        {'user': 'postgres', 'host': 'localhost', 'port': '5432', 'password': 'password'},
    ]

    dbname = "discount_app_db"
    
    print(f"Attempting to create database '{dbname}'...")

    for config in configs:
        try:
            print(f"Trying to connect as user='{config['user']}'...")
            # Connect to 'postgres' db to create new db
            conn = psycopg2.connect(
                dbname='postgres',
                user=config['user'],
                host=config['host'],
                port=config['port'],
                password=config['password']
            )
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            cursor = conn.cursor()
            
            # Check if db exists
            cursor.execute(f"SELECT 1 FROM pg_catalog.pg_database WHERE datname = '{dbname}'")
            exists = cursor.fetchone()
            
            if not exists:
                cursor.execute(f"CREATE DATABASE {dbname}")
                print(f"✅ Database '{dbname}' created successfully!")
            else:
                print(f"ℹ️  Database '{dbname}' already exists.")
            
            cursor.close()
            conn.close()
            
            # If successful, print the .env config
            print("\nSUCCESS! Update your .env file with these values:")
            print("-" * 30)
            print(f"DB_NAME={dbname}")
            print(f"DB_USER={config['user']}")
            print(f"DB_PASSWORD={config['password']}")
            print(f"DB_HOST={config['host']}")
            print(f"DB_PORT={config['port']}")
            print("-" * 30)
            return True

        except Exception as e:
            print(f"❌ Failed with user '{config['user']}': {e}")
            continue

    print("\n❌ Could not connect to PostgreSQL automatically.")
    print("Please ensure PostgreSQL is running and you know your username/password.")
    return False

if __name__ == "__main__":
    create_database()
