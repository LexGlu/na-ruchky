from django.conf import settings
from django.core.files.storage import FileSystemStorage
from storages.backends.gcloud import GoogleCloudStorage
from functools import lru_cache
from typing import Union

from ruchky_backend.helpers.logger import logger


class MediaRootGoogleCloudStorage(GoogleCloudStorage):
    """Google Cloud Storage backend configured for media files."""

    location = "media"
    file_overwrite = False


class StorageProvider:
    """
    Singleton storage provider that automatically selects the appropriate storage backend
    based on Django settings.
    """

    _instance = None
    _storage: Union[FileSystemStorage, MediaRootGoogleCloudStorage] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize_storage()
        return cls._instance

    def _initialize_storage(self) -> None:
        """Initialize the appropriate storage backend."""
        if settings.DEBUG:
            self._storage = FileSystemStorage()
            logger.info("Initialized FileSystemStorage for development")
            return

        try:
            self._storage = MediaRootGoogleCloudStorage(
                bucket_name=settings.GS_BUCKET_NAME
            )
            logger.info(
                f"Initialized Google Cloud Storage with bucket: {settings.GS_BUCKET_NAME}"
            )
        except Exception as e:
            logger.error(
                f"Error initializing Google Cloud Storage: {e}. Falling back to FileSystemStorage"
            )
            self._storage = FileSystemStorage()

    @property
    def storage(self) -> Union[FileSystemStorage, MediaRootGoogleCloudStorage]:
        """Get the configured storage backend."""
        return self._storage

    def __getattr__(self, name):
        """Delegate all unknown attributes to the storage backend."""
        return getattr(self._storage, name)


@lru_cache(maxsize=None)
def get_storage_provider() -> StorageProvider:
    """Get the singleton StorageProvider instance."""
    return StorageProvider()


storage = get_storage_provider()
