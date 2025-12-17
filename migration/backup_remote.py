import os
import subprocess
import sys
from datetime import datetime

# Add parent directory to path to import config if needed, 
# but simpler to just read .env directly or use python-dotenv
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(__file__), '..', 'backend', '.env'))
except ImportError:
    print("python-dotenv not found. Please install it: pip install python-dotenv")
    # Fallback: manual parsing or assume env vars are set
    pass

def backup_db():
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("Error: DATABASE_URL not found in environment.")
        sys.exit(1)

    # Create backups directory
    backup_dir = os.path.join(os.path.dirname(__file__), '..', 'backups')
    os.makedirs(backup_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    backup_file = os.path.join(backup_dir, f"backup_{timestamp}.sql")
    
    # Docker command to run pg_dump
    # We use the postgres:17-alpine image to match the DB version roughly
    cmd = [
        "docker", "run", "--rm", 
        "-e", f"PGPASSWORD={db_url.split(':')[2].split('@')[0]}", # Extract password roughly or pass full URL
        "postgres:17-alpine", 
        "pg_dump", 
        db_url,
        "-f", "/tmp/dump.sql"
    ]
    
    # Actually, piping stdout is easier than mounting volumes for a single file
    # docker run --rm postgres:17-alpine pg_dump "db_url" > backup_file
    
    print(f"Backing up to {backup_file}...")
    
    try:
        with open(backup_file, "w") as f:
            subprocess.check_call(
                ["docker", "run", "--rm", "postgres:17-alpine", "pg_dump", db_url], 
                stdout=f
            )
        print("Backup successful (via Docker)!")
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"Docker backup failed: {e}")
        print("Attempting fallback: Backup using Python/Pandas...")
        backup_with_pandas(db_url, backup_dir, timestamp)

def backup_with_pandas(db_url, backup_dir, timestamp):
    try:
        import pandas as pd
        from sqlalchemy import create_engine, inspect
        
        # Adjust URL for sqlalchemy (asyncpg -> psycopg2 or just remove +asyncpg if using default)
        # But we have psycopg2-binary installed, so we can use postgresql://
        if "postgresql+asyncpg" in db_url:
            db_url = db_url.replace("postgresql+asyncpg", "postgresql")
        
        # Fix SSL parameter for psycopg2 (asyncpg uses ssl=require, psycopg2 uses sslmode=require)
        if "ssl=require" in db_url:
            db_url = db_url.replace("ssl=require", "sslmode=require")
            
        engine = create_engine(db_url)
        inspector = inspect(engine)
        table_names = inspector.get_table_names()
        
        data = {}
        for table in table_names:
            print(f"Exporting table: {table}")
            df = pd.read_sql_table(table, engine)
            # Convert datetime objects to string for JSON serialization
            data[table] = df.to_dict(orient="records")
            
        import json
        json_backup_file = os.path.join(backup_dir, f"backup_{timestamp}.json")
        
        # Custom JSON encoder for dates
        class DateTimeEncoder(json.JSONEncoder):
            def default(self, o):
                if isinstance(o, (datetime.date, datetime.datetime)):
                    return o.isoformat()
                return super().default(o)

        with open(json_backup_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2, cls=DateTimeEncoder)
            
        print(f"Backup successful (via Pandas)! Saved to {json_backup_file}")
        
    except Exception as e:
        print(f"Pandas backup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    backup_db()
