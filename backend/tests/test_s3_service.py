"""Unit tests for S3 Service with caching."""
import io
import pytest
from unittest.mock import MagicMock, patch
from botocore.exceptions import ClientError


class TestLRUCache:
    """Tests for LRU cache implementation."""

    def test_cache_put_and_get(self):
        """Test basic cache put and get operations."""
        from app.services.s3 import LRUCache
        
        cache = LRUCache(max_size=10, ttl_seconds=3600)
        data = b"test image data"
        
        cache.put("test.jpg", data)
        result = cache.get("test.jpg")
        
        assert result == data

    def test_cache_miss_returns_none(self):
        """Test that cache miss returns None."""
        from app.services.s3 import LRUCache
        
        cache = LRUCache(max_size=10, ttl_seconds=3600)
        result = cache.get("nonexistent.jpg")
        
        assert result is None

    def test_cache_eviction_when_full(self):
        """Test that oldest items are evicted when cache is full."""
        from app.services.s3 import LRUCache
        
        cache = LRUCache(max_size=2, ttl_seconds=3600)
        
        cache.put("first.jpg", b"first")
        cache.put("second.jpg", b"second")
        cache.put("third.jpg", b"third")  # Should evict "first"
        
        assert cache.get("first.jpg") is None
        assert cache.get("second.jpg") == b"second"
        assert cache.get("third.jpg") == b"third"

    def test_cache_lru_ordering(self):
        """Test that accessing items moves them to end (most recently used)."""
        from app.services.s3 import LRUCache
        
        cache = LRUCache(max_size=2, ttl_seconds=3600)
        
        cache.put("first.jpg", b"first")
        cache.put("second.jpg", b"second")
        
        # Access "first" to make it recently used
        cache.get("first.jpg")
        
        # Add third item - should evict "second" (least recently used)
        cache.put("third.jpg", b"third")
        
        assert cache.get("first.jpg") == b"first"
        assert cache.get("second.jpg") is None
        assert cache.get("third.jpg") == b"third"

    def test_cache_ttl_expiration(self):
        """Test that expired items are not returned."""
        from app.services.s3 import LRUCache
        import time
        
        cache = LRUCache(max_size=10, ttl_seconds=1)  # 1 second TTL
        
        cache.put("test.jpg", b"data")
        assert cache.get("test.jpg") == b"data"
        
        # Wait for expiration
        time.sleep(1.1)
        assert cache.get("test.jpg") is None

    def test_cache_invalidate(self):
        """Test cache invalidation."""
        from app.services.s3 import LRUCache
        
        cache = LRUCache(max_size=10, ttl_seconds=3600)
        
        cache.put("test.jpg", b"data")
        cache.invalidate("test.jpg")
        
        assert cache.get("test.jpg") is None

    def test_cache_size_property(self):
        """Test cache size property."""
        from app.services.s3 import LRUCache
        
        cache = LRUCache(max_size=10, ttl_seconds=3600)
        
        assert cache.size == 0
        cache.put("a.jpg", b"a")
        assert cache.size == 1
        cache.put("b.jpg", b"b")
        assert cache.size == 2


class TestS3Service:
    """Tests for S3Service with mocked boto3."""

    @patch('app.services.s3.boto3.client')
    def test_get_file_success(self, mock_boto_client):
        """Test successful file retrieval from S3."""
        from app.services.s3 import S3Service
        
        # Setup mock
        mock_s3 = MagicMock()
        mock_boto_client.return_value = mock_s3
        mock_body = MagicMock()
        mock_body.read.return_value = b"image data"
        mock_s3.get_object.return_value = {'Body': mock_body}
        
        service = S3Service()
        result = service.get_file("test.jpg", use_cache=False)
        
        assert result is not None
        assert result.read() == b"image data"
        mock_s3.get_object.assert_called_once()

    @patch('app.services.s3.boto3.client')
    def test_get_file_uses_cache(self, mock_boto_client):
        """Test that cache is used on second request."""
        from app.services.s3 import S3Service
        
        mock_s3 = MagicMock()
        mock_boto_client.return_value = mock_s3
        mock_body = MagicMock()
        mock_body.read.return_value = b"cached data"
        mock_s3.get_object.return_value = {'Body': mock_body}
        
        service = S3Service()
        
        # First call - should hit S3
        result1 = service.get_file("cache_test.jpg", use_cache=True)
        assert result1.read() == b"cached data"
        
        # Second call - should use cache (S3 not called again)
        result2 = service.get_file("cache_test.jpg", use_cache=True)
        assert result2.read() == b"cached data"
        
        # S3 should only be called once
        assert mock_s3.get_object.call_count == 1

    @patch('app.services.s3.boto3.client')
    def test_get_file_not_found(self, mock_boto_client):
        """Test handling of non-existent file."""
        from app.services.s3 import S3Service
        
        mock_s3 = MagicMock()
        mock_boto_client.return_value = mock_s3
        mock_s3.get_object.side_effect = ClientError(
            {'Error': {'Code': 'NoSuchKey', 'Message': 'Not found'}},
            'GetObject'
        )
        
        service = S3Service()
        result = service.get_file("nonexistent.jpg")
        
        assert result is None

    @patch('app.services.s3.boto3.client')
    def test_upload_file_success(self, mock_boto_client):
        """Test successful file upload."""
        from app.services.s3 import S3Service
        
        mock_s3 = MagicMock()
        mock_boto_client.return_value = mock_s3
        
        service = S3Service()
        file_obj = io.BytesIO(b"file content")
        
        result = service.upload_file(file_obj, "uploaded.jpg")
        
        # Result should contain the filename (may include S3_PUBLIC_DOMAIN prefix)
        assert result is not None
        assert "uploaded.jpg" in result
        mock_s3.upload_fileobj.assert_called_once()

    @patch('app.services.s3.boto3.client')
    def test_upload_invalidates_cache(self, mock_boto_client):
        """Test that upload invalidates cache for that file."""
        from app.services.s3 import S3Service
        
        mock_s3 = MagicMock()
        mock_boto_client.return_value = mock_s3
        
        service = S3Service()
        # Pre-populate cache
        service._cache.put("test.jpg", b"old data")
        
        # Upload new version
        service.upload_file(io.BytesIO(b"new data"), "test.jpg")
        
        # Cache should be invalidated
        assert service._cache.get("test.jpg") is None

    @patch('app.services.s3.boto3.client')
    def test_generate_presigned_url(self, mock_boto_client):
        """Test presigned URL generation."""
        from app.services.s3 import S3Service
        
        mock_s3 = MagicMock()
        mock_boto_client.return_value = mock_s3
        mock_s3.generate_presigned_url.return_value = "https://presigned-url.com/test.jpg"
        
        service = S3Service()
        result = service.generate_presigned_url("test.jpg")
        
        assert result == "https://presigned-url.com/test.jpg"

    @patch('app.services.s3.boto3.client')
    def test_file_exists_true(self, mock_boto_client):
        """Test file_exists returns True for existing file."""
        from app.services.s3 import S3Service
        
        mock_s3 = MagicMock()
        mock_boto_client.return_value = mock_s3
        
        service = S3Service()
        result = service.file_exists("existing.jpg")
        
        assert result is True

    @patch('app.services.s3.boto3.client')
    def test_file_exists_false(self, mock_boto_client):
        """Test file_exists returns False for non-existing file."""
        from app.services.s3 import S3Service
        
        mock_s3 = MagicMock()
        mock_boto_client.return_value = mock_s3
        mock_s3.head_object.side_effect = ClientError(
            {'Error': {'Code': '404', 'Message': 'Not found'}},
            'HeadObject'
        )
        
        service = S3Service()
        result = service.file_exists("nonexistent.jpg")
        
        assert result is False

    @patch('app.services.s3.boto3.client')
    def test_cache_stats(self, mock_boto_client):
        """Test cache statistics."""
        from app.services.s3 import S3Service
        
        mock_s3 = MagicMock()
        mock_boto_client.return_value = mock_s3
        
        service = S3Service()
        stats = service.cache_stats
        
        assert "size" in stats
        assert "max_size" in stats
        assert "ttl_seconds" in stats
        assert stats["max_size"] == 100
        assert stats["ttl_seconds"] == 3600
