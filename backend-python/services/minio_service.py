from minio import Minio
from minio.error import S3Error
from typing import Optional
from datetime import timedelta
from config.database import settings


class MinioService:
    def __init__(self):
        self._client = None

    def _get_client(self) -> Minio:
        """Get or create MinIO client."""
        if self._client is None:
            self._client = Minio(
                endpoint=settings.minio_endpoint,
                access_key=settings.minio_access_key,
                secret_key=settings.minio_secret_key,
                secure=settings.minio_secure
            )
        return self._client

    def list_buckets(self) -> list[dict]:
        """List all buckets."""
        client = self._get_client()
        buckets = client.list_buckets()
        return [
            {
                "name": b.name,
                "creation_date": b.creation_date.isoformat() if b.creation_date else None
            }
            for b in buckets
        ]

    def list_objects(
        self,
        bucket: str,
        prefix: str = "",
        recursive: bool = False
    ) -> list[dict]:
        """List objects in bucket with optional prefix."""
        client = self._get_client()
        objects = client.list_objects(
            bucket_name=bucket,
            prefix=prefix,
            recursive=recursive
        )

        result = []
        for obj in objects:
            result.append({
                "name": obj.object_name,
                "size": obj.size,
                "is_dir": obj.is_dir,
                "last_modified": obj.last_modified.isoformat() if obj.last_modified else None,
                "etag": obj.etag
            })

        return result

    def get_object_info(self, bucket: str, object_name: str) -> dict:
        """Get detailed object information."""
        client = self._get_client()
        stat = client.stat_object(bucket_name=bucket, object_name=object_name)
        return {
            "name": stat.object_name,
            "size": stat.size,
            "content_type": stat.content_type,
            "last_modified": stat.last_modified.isoformat() if stat.last_modified else None,
            "etag": stat.etag,
            "metadata": dict(stat.metadata) if stat.metadata else {}
        }

    def create_bucket(self, bucket_name: str) -> bool:
        """Create a new bucket."""
        client = self._get_client()
        if not client.bucket_exists(bucket_name=bucket_name):
            client.make_bucket(bucket_name=bucket_name)
            return True
        return False

    def bucket_exists(self, bucket_name: str) -> bool:
        """Check if bucket exists."""
        client = self._get_client()
        return client.bucket_exists(bucket_name=bucket_name)

    def upload_file(
        self,
        bucket: str,
        object_name: str,
        file_path: str,
        content_type: str = None
    ):
        """Upload file to bucket."""
        client = self._get_client()
        client.fput_object(
            bucket_name=bucket,
            object_name=object_name,
            file_path=file_path,
            content_type=content_type
        )

    def download_file(self, bucket: str, object_name: str, file_path: str):
        """Download object to local file."""
        client = self._get_client()
        client.fget_object(bucket_name=bucket, object_name=object_name, file_path=file_path)

    def delete_object(self, bucket: str, object_name: str):
        """Delete object from bucket."""
        client = self._get_client()
        client.remove_object(bucket_name=bucket, object_name=object_name)

    def get_presigned_url(
        self,
        bucket: str,
        object_name: str,
        expires: int = 3600
    ) -> str:
        """Generate presigned URL for object."""
        client = self._get_client()
        return client.presigned_get_object(
            bucket_name=bucket,
            object_name=object_name,
            expires=timedelta(seconds=expires)
        )

    def test_connection(self) -> bool:
        """Test MinIO connection."""
        try:
            client = self._get_client()
            client.list_buckets()
            return True
        except Exception:
            return False


# Singleton instance
minio_service = MinioService()
