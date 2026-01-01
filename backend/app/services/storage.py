"""Google Cloud Storage service for file operations."""
from pathlib import Path
from google.cloud import storage as gcs

from app.config import settings


class StorageService:
    """Handle file uploads/downloads to Google Cloud Storage."""

    def __init__(self):
        self.bucket_name = settings.gcs_bucket
        self._client = None
        self._bucket = None

    @property
    def client(self):
        if self._client is None:
            self._client = gcs.Client(project=settings.gcp_project_id)
        return self._client

    @property
    def bucket(self):
        if self._bucket is None:
            self._bucket = self.client.bucket(self.bucket_name)
        return self._bucket

    async def upload_audio(self, data: bytes, path: str) -> str:
        """Upload audio bytes to GCS."""
        blob = self.bucket.blob(path)
        blob.upload_from_string(data, content_type="audio/mpeg")
        return f"gs://{self.bucket_name}/{path}"

    async def upload_image(self, data: bytes, path: str) -> str:
        """Upload image bytes to GCS."""
        blob = self.bucket.blob(path)
        blob.upload_from_string(data, content_type="image/jpeg")
        # Return public URL
        blob.make_public()
        return blob.public_url

    async def upload_file(self, local_path: Path, gcs_path: str) -> str:
        """Upload local file to GCS."""
        blob = self.bucket.blob(gcs_path)
        blob.upload_from_filename(str(local_path))
        return f"gs://{self.bucket_name}/{gcs_path}"

    async def download(self, gcs_path: str) -> bytes:
        """Download file from GCS as bytes."""
        # Handle both gs:// URLs and plain paths
        if gcs_path.startswith("gs://"):
            path = gcs_path.replace(f"gs://{self.bucket_name}/", "")
        else:
            path = gcs_path
        
        blob = self.bucket.blob(path)
        return blob.download_as_bytes()

    async def download_to_file(self, gcs_path: str, local_path: Path) -> None:
        """Download file from GCS to local path."""
        if gcs_path.startswith("gs://"):
            path = gcs_path.replace(f"gs://{self.bucket_name}/", "")
        else:
            path = gcs_path
        
        blob = self.bucket.blob(path)
        blob.download_to_filename(str(local_path))

    async def list_files(self, prefix: str) -> list[str]:
        """List files in GCS with given prefix."""
        blobs = self.client.list_blobs(self.bucket_name, prefix=prefix)
        return [f"gs://{self.bucket_name}/{blob.name}" for blob in blobs]

    async def get_signed_url(self, path: str, expiration_minutes: int = 60) -> str:
        """Generate signed URL for temporary access."""
        from datetime import timedelta
        
        if path.startswith("gs://"):
            path = path.replace(f"gs://{self.bucket_name}/", "")
        
        blob = self.bucket.blob(path)
        url = blob.generate_signed_url(
            version="v4",
            expiration=timedelta(minutes=expiration_minutes),
            method="GET"
        )
        return url

    async def delete(self, path: str) -> None:
        """Delete file from GCS."""
        if path.startswith("gs://"):
            path = path.replace(f"gs://{self.bucket_name}/", "")
        
        blob = self.bucket.blob(path)
        blob.delete()


# Singleton instance
storage = StorageService()
