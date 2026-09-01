import shutil
from collections.abc import Iterator
from functools import lru_cache
from pathlib import Path
from typing import BinaryIO, Protocol

import boto3

from app.core.config import get_settings


class StorageBackend(Protocol):
    def save(self, file: BinaryIO, key: str, content_type: str) -> None: ...
    def iter_bytes(self, key: str, chunk_size: int = 1024 * 1024) -> Iterator[bytes]: ...
    def delete(self, key: str) -> None: ...


class LocalFilesystemStorage:
    """Keeps document bytes on the operator's own disk -- the default, privacy-first backend."""

    def __init__(self, base_path: Path):
        self.base_path = base_path

    def _resolve(self, key: str) -> Path:
        return self.base_path / key

    def save(self, file: BinaryIO, key: str, content_type: str) -> None:
        path = self._resolve(key)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("wb") as dest:
            shutil.copyfileobj(file, dest)

    def iter_bytes(self, key: str, chunk_size: int = 1024 * 1024) -> Iterator[bytes]:
        with self._resolve(key).open("rb") as source:
            while chunk := source.read(chunk_size):
                yield chunk

    def delete(self, key: str) -> None:
        self._resolve(key).unlink(missing_ok=True)


class S3CompatibleStorage:
    """Works against AWS S3, MinIO, Backblaze B2, or anything else speaking the S3 API."""

    def __init__(
        self,
        bucket: str,
        region: str,
        endpoint_url: str | None,
        access_key_id: str,
        secret_access_key: str,
    ):
        self.bucket = bucket
        self.client = boto3.client(
            "s3",
            region_name=region,
            endpoint_url=endpoint_url or None,
            aws_access_key_id=access_key_id or None,
            aws_secret_access_key=secret_access_key or None,
        )

    def save(self, file: BinaryIO, key: str, content_type: str) -> None:
        self.client.upload_fileobj(file, self.bucket, key, ExtraArgs={"ContentType": content_type})

    def iter_bytes(self, key: str, chunk_size: int = 1024 * 1024) -> Iterator[bytes]:
        body = self.client.get_object(Bucket=self.bucket, Key=key)["Body"]
        while chunk := body.read(chunk_size):
            yield chunk

    def delete(self, key: str) -> None:
        self.client.delete_object(Bucket=self.bucket, Key=key)


@lru_cache
def get_storage_backend() -> StorageBackend:
    settings = get_settings()
    if settings.storage_backend == "s3":
        return S3CompatibleStorage(
            bucket=settings.s3_bucket,
            region=settings.s3_region,
            endpoint_url=settings.s3_endpoint_url,
            access_key_id=settings.s3_access_key_id,
            secret_access_key=settings.s3_secret_access_key,
        )
    return LocalFilesystemStorage(Path(settings.document_storage_path))
