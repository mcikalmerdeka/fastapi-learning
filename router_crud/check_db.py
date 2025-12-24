import os
from dotenv import load_dotenv

load_dotenv()

import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Default credentials based upon database.py
# Change these if your local setup is different
params = {
    "user": "postgres",
    "password": os.getenv("DATABASE_PASSWORD"),
    "host": "localhost",
    "port": "5432"
}

try:
    # Connect to default 'postgres' db to check if server is up
    print(f"Attempting to connect to PostgreSQL at {params['host']}:{params['port']} as {params['user']}...")
    conn = psycopg2.connect(**params, dbname="postgres")
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    print("SUCCESS: PostgreSQL server is running and accessible.")
    
    # Check if 'fastapi_db' exists
    cur.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = 'fastapi_db'")
    exists = cur.fetchone()
    
    if not exists:
        print("Creating database 'fastapi_db'...")
        cur.execute(sql.SQL("CREATE DATABASE fastapi_db"))
        print("SUCCESS: Database 'fastapi_db' created.")
    else:
        print("SUCCESS: Database 'fastapi_db' already exists.")
        
    cur.close()
    conn.close()
    
except Exception as e:
    print(f"FAILURE: Could not connect to PostgreSQL. Error: {e}")
    print("Please ensure your PostgreSQL service is started and the credentials in check_db.py (and database.py) match your setup.")
