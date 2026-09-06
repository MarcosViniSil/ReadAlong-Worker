from models.chunk import Chunk
from models.enum.BookStatus import BookStatus
from storage.chunkRepository.chunkRepositoryProvider import ChunkRepositoryProvider
from storage.config_db.database import Database


class ChunkRepositoryImpl(ChunkRepositoryProvider):

    def __init__(self, db: Database):
        self._db = db

    @staticmethod
    def _chunk_from_row(row: dict) -> Chunk:
        return Chunk(
            id=str(row["id"]),
            page_id=str(row["page_id"]),
            sequence=row["sequence"],
            text=row["text"],
            status=BookStatus(row["status"]),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    async def get_by_id(self, chunk_id) -> Chunk | None:
        async with self._db.transaction() as tx:
            cursor = await tx.execute(
                "SELECT * FROM chunks WHERE id = %s::uuid",
                [chunk_id],
            )
            row = await cursor.fetchone()
        return self._chunk_from_row(row) if row else None

    async def update_status(self, chunk_id, status: BookStatus) -> None:
        async with self._db.transaction() as tx:
            await tx.execute(
                "UPDATE chunks SET status = %s, updated_at = now() WHERE id = %s::uuid",
                [str(status), chunk_id],
            )
