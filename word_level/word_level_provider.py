from abc import ABC, abstractmethod

from models.wordLevelTranscription import WordLevelTranscription


class WordLevelProvider(ABC):

    @abstractmethod
    def generate_word_mapping(self, audio_path:str) -> WordLevelTranscription:
        pass