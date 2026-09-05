from dataclasses import dataclass, field

from models.segments import Segments


@dataclass
class WordLevelTranscription:
    segments: list[Segments] = field(default_factory=list)
    language: str = ""
