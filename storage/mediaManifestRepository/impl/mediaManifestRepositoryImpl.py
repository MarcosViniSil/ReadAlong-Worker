from models.enum.BookStatus import BookStatus
from models.mediaManifest import MediaManifest
from storage.audioAssetRepository.audioAssetRepositoryProvider import (
    AudioAssetRepositoryProvider,
)
from storage.config_db import Database


class MediaManifestRepositoryRepositoryImpl(AudioAssetRepositoryProvider):

    def __init__(self, db: Database):
        self._db = db

    @staticmethod
    def _media_manifest_from_row(row: dict) -> MediaManifest:
        return MediaManifest(
            id=str(row["id"]),
            book_id=str(row["book_id"]),
            chunk_id=row["chunk_id"],
            type=row["type"],
            storage_key=row["storage_key"],
            status=row["status"],
            created_at=row["created_at"],
        )

    async def create(self, media_manifest: MediaManifest) -> MediaManifest:
        async with self._db.transaction() as tx:
            cursor = await tx.execute(
                """
                INSERT INTO media_manifests (book_id, chunk_id, type, storage_key, status, created_at)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING *
                """,
                [
                    media_manifest.book_id,
                    media_manifest.chunk_id,
                    media_manifest.type,
                    media_manifest.storage_key,
                    str(media_manifest.status),
                    media_manifest.created_at,
                ],
            )

            row = await cursor.fetchone()

        return self._media_manifest_from_row(row)
