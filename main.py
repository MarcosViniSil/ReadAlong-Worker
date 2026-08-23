from provider.ttsProvider import getTTSProvider
from provider.wordlevelProvider import getWordLevelProvider


tts = getTTSProvider()
wordLevel = getWordLevelProvider()

#tts.generate("test",["Test1, this is an example of audio to became a TTS transcription"])
wordLevel.generate_word_mapping("./audio/test.wav")