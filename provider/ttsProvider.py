from tts import TTSProvider
from tts.imp.TTSProviderImpl import KokoroProviderImpl


def getTTSProvider() -> TTSProvider:
    return KokoroProviderImpl()
