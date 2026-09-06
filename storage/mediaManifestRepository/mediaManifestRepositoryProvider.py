from abc import ABC, abstractmethod

from models.AudioAsset import AudioAsset
from models.enum import BookStatus
from models.mediaManifest import MediaManifest


class MediaManifestRepositoryProvider(ABC):

    @abstractmethod
    async def create(self, audio_asset: MediaManifest):
        pass
