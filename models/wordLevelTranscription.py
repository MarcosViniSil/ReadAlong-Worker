from dataclasses import dataclass, field


@dataclass
class WordLevelTranscription:
    segments: list[str] = field(default_factory=dict)
    language: str = ""
