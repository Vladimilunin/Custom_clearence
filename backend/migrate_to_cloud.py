import psycopg2
import boto3
import os
import sys

# Configuration
DATABASE_URL = "postgresql://neondb_owner:npg_Ir8kd1ByDSuQ@ep-bitter-night-ahz06l2w-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require"
S3_ENDPOINT = "https://a3e756743a64a62e93a9b990fde76041.r2.cloudflarestorage.com"
S3_ACCESS_KEY = "ca510f34035fb42d3c995997d5c681f4"
S3_SECRET_KEY = "d413607932eb1e783befdf6903005db979e0c2904ba37e239d0bd57e34518b7a"
S3_BUCKET_NAME = "customs-images"

SQL_FILE_PATH = r"d:\Work\_develop\_gen_for_ tamozh\_dev\backups\backup_2025-11-23_04-28.sql"
IMAGES_DIR = r"d:\Work\_develop\_gen_for_ tamozh\_dev\_изображения"

def get_s3_client():
    return boto3.client(
        's3',
        endpoint_url=S3_ENDPOINT,
        aws_access_key_id=S3_ACCESS_KEY,
        aws_secret_access_key=S3_SECRET_KEY
    )

def upload_image_to_s3(s3, filename):
    local_path = os.path.join(IMAGES_DIR, filename)
    if not os.path.exists(local_path):
        # Try finding it recursively or with slight name variations if needed
        # But for now, strict match as per dump
        print(f"   ⚠️ Image not found locally: {filename}")
        return False
    
    try:
        content_type = "image/jpeg"
        if filename.lower().endswith(".webp"):
            content_type = "image/webp"
        elif filename.lower().endswith(".png"):
            content_type = "image/png"
            
        print(f"   🚀 Uploading {filename} to S3...")
        with open(local_path, "rb") as f:
            s3.upload_fileobj(
                f, 
                S3_BUCKET_NAME, 
                filename,
                ExtraArgs={'ContentType': content_type}
            )
        return True
    except Exception as e:
        print(f"   ❌ Failed to upload {filename}: {e}")
        return False

def migrate():
    print("🔌 Connecting to Database...")
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
    except Exception as e:
        print(f"❌ DB Connection failed: {e}")
        return

    print("🔌 Connecting to S3...")
    s3 = get_s3_client()

    print("📖 Reading SQL Dump...")
    with open(SQL_FILE_PATH, 'r', encoding='utf-8') as f:
        sql_content = f.read()

    # 1. Clean existing tables
    print("🧹 Cleaning existing tables...")
    cur.execute("DROP TABLE IF EXISTS public.parts CASCADE;")
    cur.execute("DROP TABLE IF EXISTS public.alembic_version CASCADE;")
    conn.commit()

    # 2. Parse and Execute SQL
    # Filter out pg_dump specific commands starting with backslash, BUT keep \. (end of data)
    lines = []
    for line in sql_content.splitlines():
        stripped = line.strip()
        if stripped.startswith("\\") and stripped != "\\.":
            continue
        if "OWNER TO postgres" in line:
            continue
        lines.append(line)
    
    filtered_content = "\n".join(lines)
    
    chunks = filtered_content.split("COPY ")
    
    # Execute the first chunk (DDL)
    print("🛠️ Executing Schema DDL...")
    try:
        cur.execute(chunks[0])
        conn.commit()
    except Exception as e:
        print(f"❌ Schema execution failed: {e}")
        # Continue anyway?
    
    # Process COPY chunks
    for chunk in chunks[1:]:
        # Format: "public.table_name (columns) FROM stdin;\nData...\n\.\n\nRest of SQL"
        
        # Extract table name and columns
        line1_end = chunk.find("\n")
        header = chunk[:line1_end] # e.g. public.parts (id, ...) FROM stdin;
        
        table_name = header.split(" ")[0]
        
        # Extract data block
        data_end = chunk.find("\n\\.")
        if data_end == -1:
            print(f"⚠️ Could not find end of data for {table_name}")
            continue
            
        data_block = chunk[line1_end+1:data_end]
        
        print(f"📥 Restoring data for {table_name}...")
        
        rows = data_block.strip().split("\n")
        
        if table_name == "public.parts":
            # Columns: id, designation, name, material, weight, dimensions, description, section, image_path
            # We need to INSERT and Upload Images
            for row in rows:
                cols = row.split("\t")
                # Handle \N as None
                cols = [None if c == "\\N" else c for c in cols]
                
                # Insert into DB
                # Construct INSERT statement safely
                # id is cols[0], designation is cols[1], ..., image_path is cols[8]
                
                try:
                    cur.execute(
                        """
                        INSERT INTO public.parts 
                        (id, designation, name, material, weight, dimensions, description, section, image_path)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """,
                        cols
                    )
                except Exception as e:
                    print(f"   ❌ Insert failed for {cols[1]}: {e}")
                    conn.rollback()
                    continue
                
                # Upload Image
                image_path = cols[8]
                if image_path:
                    upload_image_to_s3(s3, image_path)
            
            conn.commit()
            print(f"✅ Restored {len(rows)} parts.")

        elif table_name == "public.alembic_version":
            # Just insert
            for row in rows:
                cols = row.split("\t")
                cur.execute("INSERT INTO public.alembic_version (version_num) VALUES (%s)", cols)
            conn.commit()
            print("✅ Restored alembic_version.")
            
        # Execute any remaining SQL after \.
        rest_of_sql = chunk[data_end+4:] # Skip \.\n\n
        if rest_of_sql.strip():
            try:
                cur.execute(rest_of_sql)
                conn.commit()
            except Exception as e:
                print(f"⚠️ Post-data SQL execution failed (indexes/sequences): {e}")

    print("\n🎉 Migration Complete!")
    conn.close()

if __name__ == "__main__":
    migrate()
