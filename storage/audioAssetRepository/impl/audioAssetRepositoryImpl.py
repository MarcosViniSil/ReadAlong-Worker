from models.AudioAsset import AudioAsset
from models.chunk import Chunk
from models.enum.BookStatus import BookStatus
from storage.audioAssetRepository.audioAssetRepositoryProvider import (
    AudioAssetRepositoryProvider,
)
from storage.config_db import Database


class AudioAssetRepositoryImpl(AudioAssetRepositoryProvider):

    def __init__(self, db: Database):
        self._db = db

    @staticmethod
    def _audio_asset_from_row(row: dict) -> AudioAsset:
        return AudioAsset(
            id=str(row["id"]),
            chunk_id=str(row["chunk_id"]),
            storage_key=row["storage_key"],
            format=row["format"],
            size=row["size"],
            status=BookStatus(row["status"]),
            created_at=row["created_at"],
        )

    async def create(self, audio_asset: AudioAsset) -> AudioAsset:
        async with self._db.transaction() as tx:
            cursor = await tx.execute(
                """
                INSERT INTO audio_assets (chunk_id, storage_key, format, size, status)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING *
                """,
                [
                    audio_asset.chunk_id,
                    audio_asset.storage_key,
                    audio_asset.format,
                    audio_asset.size,
                    str(audio_asset.status),
                ],
            )

            row = await cursor.fetchone()

        return self._audio_asset_from_row(row)
