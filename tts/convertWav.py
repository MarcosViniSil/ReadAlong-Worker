from pathlib import Path

from pydub import AudioSegment

from common.config import AUDIO_DIR
from log.loggerService import LoggerService


def convert_wav_to_mp3(wav_path: str) -> str:
    try:
        wav_file = Path(wav_path)

        LoggerService.log_info(
            "Starting WAV to MP3 conversion - WAV path: %s",
            wav_file,
        )

        if not wav_file.exists():
            LoggerService.log_error(
                "WAV file not found - path: %s, absolute path: %s",
                wav_file,
                wav_file.resolve(),
            )
            return ""

        filename = wav_file.stem

        AUDIO_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

        mp3_path = AUDIO_DIR / f"{filename}.mp3"

        LoggerService.log_debug(
            "Converting WAV to MP3 - Input: %s, Output: %s",
            wav_file,
            mp3_path,
        )

        audio = AudioSegment.from_wav(
            str(wav_file)
        )

        audio.export(
            str(mp3_path),
            format="mp3",
            bitrate="192k",
        )

        LoggerService.log_info(
            "WAV successfully converted to MP3 - Input: %s, Output: %s",
            wav_file,
            mp3_path,
        )

        wav_file.unlink(
            missing_ok=True
        )

        LoggerService.log_debug(
            "Original WAV file removed: %s",
            wav_file,
        )

        return str(mp3_path)

    except Exception as exc:
        LoggerService.log_error(
            "Error converting WAV to MP3 - Input: %s",
            wav_path,
            exc=exc,
        )
        return ""
