from abc import ABC, abstractmethod

from models.AudioAsset import AudioAsset
from models.enum import BookStatus


class AudioAssetRepositoryProvider(ABC):

    @abstractmethod
    async def create(self, audio_asset: AudioAsset):
        pass
