from minio import Minio
from minio.error import S3Error
from typing import BinaryIO, Optional
import io
from datetime import timedelta
from app.config import settings


class MinIOService:
    def __init__(self):
        self.client = Minio(
            settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_SECURE
        )
        # НЕ создаем buckets сразу при инициализации
        self._buckets_initialized = False
    
    def _ensure_buckets(self):
        """Create buckets if they don't exist (lazy initialization)"""
        if self._buckets_initialized:
            return
        
        buckets = [
            settings.MINIO_BUCKET_PRODUCTS,
            settings.MINIO_BUCKET_AVATARS
        ]
        
        for bucket in buckets:
            try:
                if not self.client.bucket_exists(bucket):
                    self.client.make_bucket(bucket)
                    # Set bucket policy to public read
                    policy = {
                        "Version": "2012-10-17",
                        "Statement": [
                            {
                                "Effect": "Allow",
                                "Principal": {"AWS": "*"},
                                "Action": ["s3:GetObject"],
                                "Resource": [f"arn:aws:s3:::{bucket}/*"]
                            }
                        ]
                    }
                    import json
                    self.client.set_bucket_policy(bucket, json.dumps(policy))
            except S3Error as e:
                print(f"Warning: Could not create bucket {bucket}: {e}")
            except Exception as e:
                print(f"Warning: Error with MinIO bucket {bucket}: {e}")
        
        self._buckets_initialized = True
    
    def upload_file(
        self,
        bucket_name: str,
        file: BinaryIO,
        file_name: str,
        content_type: str = "application/octet-stream"
    ) -> Optional[str]:
        """Upload file to MinIO"""
        try:
            # Ensure buckets exist before uploading
            self._ensure_buckets()
            
            # Get file size
            file.seek(0, 2)
            file_size = file.tell()
            file.seek(0)
            
            # Upload file
            self.client.put_object(
                bucket_name=bucket_name,
                object_name=file_name,
                data=file,
                length=file_size,
                content_type=content_type
            )
            
            # Return public URL
            url = f"http://{settings.MINIO_ENDPOINT}/{bucket_name}/{file_name}"
            return url
        except S3Error as e:
            print(f"Error uploading file: {e}")
            return None
    
    def upload_bytes(
        self,
        bucket_name: str,
        data: bytes,
        file_name: str,
        content_type: str = "application/octet-stream"
    ) -> Optional[str]:
        """Upload bytes to MinIO"""
        try:
            file_like = io.BytesIO(data)
            return self.upload_file(bucket_name, file_like, file_name, content_type)
        except Exception as e:
            print(f"Error uploading bytes: {e}")
            return None
    
    def delete_file(self, bucket_name: str, file_name: str) -> bool:
        """Delete file from MinIO"""
        try:
            self.client.remove_object(bucket_name, file_name)
            return True
        except S3Error as e:
            print(f"Error deleting file: {e}")
            return False
    
    def get_file_url(
        self,
        bucket_name: str,
        file_name: str,
        expires: timedelta = timedelta(hours=1)
    ) -> Optional[str]:
        """Get presigned URL for file"""
        try:
            url = self.client.presigned_get_object(
                bucket_name=bucket_name,
                object_name=file_name,
                expires=expires
            )
            return url
        except S3Error as e:
            print(f"Error getting file URL: {e}")
            return None
    
    def list_files(self, bucket_name: str, prefix: str = "") -> list:
        """List files in bucket"""
        try:
            objects = self.client.list_objects(bucket_name, prefix=prefix)
            return [obj.object_name for obj in objects]
        except S3Error as e:
            print(f"Error listing files: {e}")
            return []


# Create singleton instance (but don't initialize buckets yet)
minio_service = MinIOService()