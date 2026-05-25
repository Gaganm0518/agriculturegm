"""
Python script to run the MySQL database migration.
Reads backend/schema.sql and executes it against the database.
Requires the DATABASE_URL environment variable or uses the default.
"""

import os
import pymysql
from dotenv import load_dotenv

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

def get_mysql_connection():
    """Extract connection details from DATABASE_URL and return a pymysql connection."""
    db_url = os.getenv('DATABASE_URL', 'mysql+pymysql://root:password@localhost/agri_db')
    
    # Simple parse of mysql+pymysql://user:pass@host:port/dbname
    try:
        if '://' in db_url:
            parts = db_url.split('://')[1].split('/')
            credentials, host = parts[0].split('@')
            user, password = credentials.split(':')
            if ':' in host:
                host, port = host.split(':')
                port = int(port)
            else:
                port = 3306
                
            return pymysql.connect(
                host=host,
                port=port,
                user=user,
                password=password,
                client_flag=pymysql.constants.CLIENT.MULTI_STATEMENTS
            )
        return None
    except Exception as e:
        print(f"Error parsing database URL: {e}")
        return None

def run_migration():
    """Read the schema.sql file and execute it."""
    sql_file = os.path.join(os.path.dirname(__file__), 'schema.sql')
    
    if not os.path.exists(sql_file):
        print(f"Error: Could not find {sql_file}")
        return False
        
    print(f"Reading schema from: {sql_file}")
    with open(sql_file, 'r') as f:
        sql = f.read()
        
    print("Connecting to MySQL database...")
    connection = get_mysql_connection()
    
    if not connection:
        print("Failed to establish database connection. Please check your DATABASE_URL.")
        return False
        
    try:
        with connection.cursor() as cursor:
            # Execute the multi-statement SQL
            print("Executing migration...")
            cursor.execute(sql)
        connection.commit()
        print("✅ Database migration completed successfully!")
        return True
    except Exception as e:
        print(f"❌ Error during migration: {e}")
        connection.rollback()
        return False
    finally:
        connection.close()

if __name__ == '__main__':
    run_migration()
