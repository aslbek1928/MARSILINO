import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import os

def update_password():
    dbname = "postgres"
    user = "aslbek1928"
    # Current password is empty based on previous steps
    password = "" 
    host = "localhost"
    port = "5432"
    
    new_password = "aslbek10.09.2008"

    try:
        print(f"Connecting to '{dbname}' to update password for '{user}'...")
        conn = psycopg2.connect(
            dbname=dbname,
            user=user,
            host=host,
            port=port,
            password=password
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Update password
        cursor.execute(f"ALTER USER \"{user}\" WITH PASSWORD '{new_password}';")
        print(f"✅ Password for user '{user}' updated successfully!")
        
        cursor.close()
        conn.close()
        return True

    except Exception as e:
        print(f"❌ Failed to update password: {e}")
        return False

if __name__ == "__main__":
    update_password()
