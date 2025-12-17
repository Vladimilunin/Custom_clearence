import boto3
from botocore.exceptions import NoCredentialsError
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class S3Service:
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            endpoint_url=settings.S3_ENDPOINT,
            aws_access_key_id=settings.S3_ACCESS_KEY,
            aws_secret_access_key=settings.S3_SECRET_KEY
        )
        self.bucket_name = settings.S3_BUCKET_NAME

    def upload_file(self, file_obj, object_name):
        try:
            self.s3_client.upload_fileobj(
                file_obj,
                self.bucket_name,
                object_name,
                ExtraArgs={'ACL': 'public-read'} # Optional: make public if needed
            )
            # Construct the URL
            # For R2, if you have a custom domain or just use the endpoint
            # Usually R2 public URL is https://<bucket>.<account>.r2.dev/<object> if public access is on
            # Or if using a custom domain.
            # For now, let's return the object name or a constructed URL if we know the public domain.
            # Assuming we want to return the full URL if possible, but R2 public access setup varies.
            # Let's return the object key for now, or try to construct a standard URL.
            
            # If S3_PUBLIC_DOMAIN is set, use it.
            if hasattr(settings, 'S3_PUBLIC_DOMAIN') and settings.S3_PUBLIC_DOMAIN:
                 return f"{settings.S3_PUBLIC_DOMAIN}/{object_name}"
            
            return object_name
        except NoCredentialsError:
            logger.error("Credentials not available")
            return None
        except Exception as e:
            logger.error(f"Failed to upload to S3: {e}")
            return None

    def get_file(self, object_name):
        try:
            response = self.s3_client.get_object(Bucket=self.bucket_name, Key=object_name)
            return response['Body']
        except Exception as e:
            logger.error(f"Failed to get file from S3: {e}")
            return None

s3_service = S3Service()
