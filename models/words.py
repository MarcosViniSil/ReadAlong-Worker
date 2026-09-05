from dataclasses import dataclass


@dataclass
class Word:
    word: str
    start: float
    end: float
    score: float
