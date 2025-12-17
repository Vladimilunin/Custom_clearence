"""
S3/MinIO Storage Service with caching and performance optimizations.

Features:
- In-memory LRU cache for frequently accessed images
- Presigned URL generation for direct client access
- Proper error handling with typed exceptions
"""
import io
import logging
import time
from collections import OrderedDict
from typing import BinaryIO, Optional, Tuple

import boto3
from botocore.exceptions import ClientError, NoCredentialsError

from app.core.config import settings

logger = logging.getLogger(__name__)


class LRUCache:
    """Simple LRU cache with TTL support for image bytes."""
    
    def __init__(self, max_size: int = 100, ttl_seconds: int = 3600):
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self._cache: OrderedDict[str, Tuple[bytes, float]] = OrderedDict()
    
    def get(self, key: str) -> Optional[bytes]:
        """Get item from cache if exists and not expired."""
        if key not in self._cache:
            return None
        
        data, timestamp = self._cache[key]
        if time.time() - timestamp > self.ttl_seconds:
            del self._cache[key]
            return None
        
        # Move to end (most recently used)
        self._cache.move_to_end(key)
        return data
    
    def put(self, key: str, value: bytes) -> None:
        """Add item to cache, evicting oldest if full."""
        if key in self._cache:
            self._cache.move_to_end(key)
        else:
            if len(self._cache) >= self.max_size:
                self._cache.popitem(last=False)
        
        self._cache[key] = (value, time.time())
    
    def invalidate(self, key: str) -> None:
        """Remove item from cache."""
        self._cache.pop(key, None)
    
    def clear(self) -> None:
        """Clear entire cache."""
        self._cache.clear()
    
    @property
    def size(self) -> int:
        """Current cache size."""
        return len(self._cache)


class S3Service:
    """S3/MinIO storage service with caching."""
    
    # Cache settings
    CACHE_MAX_SIZE = 100  # Max items in cache
    CACHE_TTL = 3600  # 1 hour TTL
    PRESIGNED_URL_EXPIRY = 3600  # 1 hour
    
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            endpoint_url=settings.S3_ENDPOINT,
            aws_access_key_id=settings.S3_ACCESS_KEY,
            aws_secret_access_key=settings.S3_SECRET_KEY
        )
        self.bucket_name = settings.S3_BUCKET_NAME
        self._cache = LRUCache(
            max_size=self.CACHE_MAX_SIZE,
            ttl_seconds=self.CACHE_TTL
        )
        logger.info(f"S3Service initialized with cache (max={self.CACHE_MAX_SIZE}, ttl={self.CACHE_TTL}s)")

    def upload_file(self, file_obj: BinaryIO, object_name: str) -> Optional[str]:
        """
        Upload a file to S3/MinIO.
        
        Args:
            file_obj: File-like object to upload
            object_name: Target object key in bucket
            
        Returns:
            Public URL or object name on success, None on failure
        """
        try:
            self.s3_client.upload_fileobj(
                file_obj,
                self.bucket_name,
                object_name,
                ExtraArgs={'ACL': 'public-read'}
            )
            
            # Invalidate cache for this object (in case of update)
            self._cache.invalidate(object_name)
            
            # Return public URL if domain is configured
            if hasattr(settings, 'S3_PUBLIC_DOMAIN') and settings.S3_PUBLIC_DOMAIN:
                return f"{settings.S3_PUBLIC_DOMAIN}/{object_name}"

            return object_name
            
        except NoCredentialsError:
            logger.error("S3 credentials not available")
            return None
        except ClientError as e:
            logger.error(f"S3 client error uploading {object_name}: {e.response['Error']['Message']}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error uploading to S3: {e}")
            return None

    def get_file(self, object_name: str, use_cache: bool = True) -> Optional[BinaryIO]:
        """
        Get a file from S3/MinIO with caching.
        
        Args:
            object_name: Object key to retrieve
            use_cache: Whether to use in-memory cache (default True)
            
        Returns:
            File-like object (BytesIO) on success, None on failure
        """
        # Check cache first
        if use_cache:
            cached_data = self._cache.get(object_name)
            if cached_data is not None:
                logger.debug(f"Cache hit for {object_name}")
                return io.BytesIO(cached_data)
        
        try:
            response = self.s3_client.get_object(Bucket=self.bucket_name, Key=object_name)
            data = response['Body'].read()
            
            # Store in cache
            if use_cache and len(data) < 10 * 1024 * 1024:  # Only cache files < 10MB
                self._cache.put(object_name, data)
                logger.debug(f"Cached {object_name} ({len(data)} bytes)")
            
            return io.BytesIO(data)
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'NoSuchKey':
                logger.warning(f"Object not found in S3: {object_name}")
            else:
                logger.error(f"S3 client error getting {object_name}: {e.response['Error']['Message']}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error getting file from S3: {e}")
            return None

    def generate_presigned_url(self, object_name: str, expiry: int = None) -> Optional[str]:
        """
        Generate a presigned URL for direct client access.
        
        This bypasses the backend for image loading, improving performance.
        
        Args:
            object_name: Object key
            expiry: URL expiry time in seconds (default: 1 hour)
            
        Returns:
            Presigned URL string or None on failure
        """
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': object_name},
                ExpiresIn=expiry or self.PRESIGNED_URL_EXPIRY
            )
            return url
        except ClientError as e:
            logger.error(f"Failed to generate presigned URL for {object_name}: {e}")
            return None

    def file_exists(self, object_name: str) -> bool:
        """
        Check if a file exists in the bucket.
        
        Args:
            object_name: Object key to check
            
        Returns:
            True if exists, False otherwise
        """
        try:
            self.s3_client.head_object(Bucket=self.bucket_name, Key=object_name)
            return True
        except ClientError:
            return False

    @property
    def cache_stats(self) -> dict:
        """Get cache statistics."""
        return {
            "size": self._cache.size,
            "max_size": self.CACHE_MAX_SIZE,
            "ttl_seconds": self.CACHE_TTL
        }


s3_service = S3Service()
