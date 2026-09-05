from dataclasses import dataclass
import datetime
from models.enum import BookStatus


@dataclass
class ChunkWord:
    text: str
    start: float
    end: float


@dataclass
class ChunkAudio:
    start: float
    end: float
    words: list[ChunkWord]
