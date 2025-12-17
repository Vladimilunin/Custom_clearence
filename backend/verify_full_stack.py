import os
import asyncio
import asyncpg
import boto3
from botocore.client import Config

# Env vars from deploy_cloud_run.ps1
DATABASE_URL = "postgresql://neondb_owner:npg_Ir8kd1ByDSuQ@ep-bitter-night-ahz06l2w-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require"
S3_ENDPOINT = "https://a3e756743a64a62e93a9b990fde76041.r2.cloudflarestorage.com"
S3_ACCESS_KEY = "ca510f34035fb42d3c995997d5c681f4"
S3_SECRET_KEY = "d413607932eb1e783befdf6903005db979e0c2904ba37e239d0bd57e34518b7a"
S3_BUCKET_NAME = "customs-images"

async def check_db():
    print("Checking Database connection...")
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        version = await conn.fetchval("SELECT version()")
        print(f"✅ Database connected: {version}")
        await conn.close()
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def check_s3():
    print("Checking S3 connection...")
    try:
        s3 = boto3.client(
            's3',
            endpoint_url=S3_ENDPOINT,
            aws_access_key_id=S3_ACCESS_KEY,
            aws_secret_access_key=S3_SECRET_KEY,
            config=Config(signature_version='s3v4'),
            region_name='auto'
        )
        response = s3.list_buckets()
        buckets = [b['Name'] for b in response['Buckets']]
        print(f"✅ S3 connected. Buckets: {buckets}")
        
        # Check specific bucket
        if S3_BUCKET_NAME in buckets:
            print(f"✅ Bucket '{S3_BUCKET_NAME}' found.")
            # List objects
            objs = s3.list_objects_v2(Bucket=S3_BUCKET_NAME, MaxKeys=5)
            if 'Contents' in objs:
                print(f"✅ Found {len(objs['Contents'])} objects in bucket.")
            else:
                print("⚠️ Bucket is empty or no objects found.")
        else:
            print(f"❌ Bucket '{S3_BUCKET_NAME}' not found!")
            
        return True
    except Exception as e:
        print(f"❌ S3 connection failed: {e}")
        return False

async def main():
    db_ok = await check_db()
    s3_ok = check_s3()
    
    if db_ok and s3_ok:
        print("\n🎉 Backend infrastructure verification SUCCESSFUL!")
    else:
        print("\n❌ Backend infrastructure verification FAILED.")

if __name__ == "__main__":
    asyncio.run(main())
