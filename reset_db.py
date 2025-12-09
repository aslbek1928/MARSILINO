import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import os
from dotenv import load_dotenv

load_dotenv()

def reset_database():
    # Get config from env or defaults
    dbname = os.getenv('DB_NAME', 'discount_app_db')
    user = os.getenv('DB_USER', 'postgres')
    password = os.getenv('DB_PASSWORD', 'postgres')
    host = os.getenv('DB_HOST', 'localhost')
    port = os.getenv('DB_PORT', '5432')

    print(f"Attempting to reset database '{dbname}'...")

    try:
        # Connect to 'postgres' db to drop/create target db
        conn = psycopg2.connect(
            dbname='postgres',
            user=user,
            host=host,
            port=port,
            password=password
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Terminate all other connections to the database
        print(f"Terminating active connections to '{dbname}'...")
        cursor.execute(f"""
            SELECT pg_terminate_backend(pg_stat_activity.pid)
            FROM pg_stat_activity
            WHERE pg_stat_activity.datname = '{dbname}'
            AND pid <> pg_backend_pid();
        """)
        
        # Drop db if exists
        print(f"Dropping database '{dbname}' if it exists...")
        cursor.execute(f"DROP DATABASE IF EXISTS {dbname}")
        
        # Create db
        print(f"Creating database '{dbname}'...")
        cursor.execute(f"CREATE DATABASE {dbname}")
        
        print(f"✅ Database '{dbname}' reset successfully!")
        
        cursor.close()
        conn.close()
        return True

    except Exception as e:
        print(f"❌ Failed to reset database: {e}")
        return False

if __name__ == "__main__":
    reset_database()
