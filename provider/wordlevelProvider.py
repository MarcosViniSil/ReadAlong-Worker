from word_level.impl.word_level_impl import WordLevelImpl
from word_level.word_level_provider import WordLevelProvider


def getWordLevelProvider() -> WordLevelProvider:
    return WordLevelImpl()
