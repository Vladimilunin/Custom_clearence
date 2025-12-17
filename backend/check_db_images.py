import asyncio
import asyncpg
import os

# Env vars
DATABASE_URL = "postgresql://neondb_owner:npg_Ir8kd1ByDSuQ@ep-bitter-night-ahz06l2w-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require"

async def check_parts():
    conn = await asyncpg.connect(DATABASE_URL)
    # Check specific parts from screenshot
    parts_to_check = ['R1.003', 'R1.02.00.001', 'R1.02.00.002']
    for p in parts_to_check:
        row = await conn.fetchrow("SELECT designation, image_path FROM parts WHERE designation = $1", p)
        if row:
            print(f"Part: {row['designation']}, Image Path: {row['image_path']}")
        else:
            print(f"Part: {p} NOT FOUND in DB")
    await conn.close()

def list_s3_objects():
    import boto3
    from botocore.client import Config
    
    S3_ENDPOINT = "https://a3e756743a64a62e93a9b990fde76041.r2.cloudflarestorage.com"
    S3_ACCESS_KEY = "ca510f34035fb42d3c995997d5c681f4"
    S3_SECRET_KEY = "d413607932eb1e783befdf6903005db979e0c2904ba37e239d0bd57e34518b7a"
    S3_BUCKET_NAME = "customs-images"
    
    s3 = boto3.client(
        's3',
        endpoint_url=S3_ENDPOINT,
        aws_access_key_id=S3_ACCESS_KEY,
        aws_secret_access_key=S3_SECRET_KEY,
        config=Config(signature_version='s3v4'),
        region_name='auto'
    )
    
    print("\n--- S3 Objects ---")
    response = s3.list_objects_v2(Bucket=S3_BUCKET_NAME)
    if 'Contents' in response:
        for obj in response['Contents']:
            print(f"Key: {obj['Key']}, Size: {obj['Size']}")
    else:
        print("Bucket is empty.")

def check_s3_file(key):
    import boto3
    from botocore.client import Config
    from botocore.exceptions import ClientError
    
    S3_ENDPOINT = "https://a3e756743a64a62e93a9b990fde76041.r2.cloudflarestorage.com"
    S3_ACCESS_KEY = "ca510f34035fb42d3c995997d5c681f4"
    S3_SECRET_KEY = "d413607932eb1e783befdf6903005db979e0c2904ba37e239d0bd57e34518b7a"
    S3_BUCKET_NAME = "customs-images"
    
    s3 = boto3.client(
        's3',
        endpoint_url=S3_ENDPOINT,
        aws_access_key_id=S3_ACCESS_KEY,
        aws_secret_access_key=S3_SECRET_KEY,
        config=Config(signature_version='s3v4'),
        region_name='auto'
    )
    
    print(f"Checking for {key} in S3...")
    try:
        s3.head_object(Bucket=S3_BUCKET_NAME, Key=key)
        print(f"✅ Found {key} in S3")
    except ClientError as e:
        if e.response['Error']['Code'] == "404":
            print(f"❌ {key} NOT FOUND in S3")
        else:
            print(f"❌ Error checking S3: {e}")

if __name__ == "__main__":
    # asyncio.run(check_parts())
    check_s3_file("R1.003.webp")
