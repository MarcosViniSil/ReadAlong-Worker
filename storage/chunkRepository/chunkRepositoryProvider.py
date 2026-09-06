from abc import ABC, abstractmethod

from models.chunk import Chunk
from models.enum import BookStatus


class ChunkRepositoryProvider(ABC):

    @abstractmethod
    async def get_by_id(self, chunk_id: int):
        pass

    @abstractmethod
    async def update_status(self, chunk_id:int, status: BookStatus):
        pass