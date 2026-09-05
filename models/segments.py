from dataclasses import dataclass

from models.words import Word


@dataclass
class Segments:
    start: str
    end: str
    text: int
    words: list[Word]
