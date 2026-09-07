from dataclasses import dataclass
import datetime

from models.enum import BookStatus

@dataclass
class MediaManifest:
    id: str
    chunk_id: str
    type: str
    storage_key: str
    status: BookStatus
    created_at: datetime 