"""Local Whisper transcription and microphone capture."""

from __future__ import annotations

import logging
import os
from functools import lru_cache
from pathlib import Path

import sounddevice as sd
import whisper
from scipy.io.wavfile import write

from core.config import get_secret

LOGGER = logging.getLogger(__name__)
DEFAULT_RECORD_SECONDS = 30
SAMPLE_RATE = 16000


def _configure_ffmpeg() -> None:
    ffmpeg_path = get_secret("FFMPEG_PATH")
    if ffmpeg_path:
        os.environ["PATH"] = ffmpeg_path + os.pathsep + os.environ.get("PATH", "")


@lru_cache(maxsize=1)
def _get_whisper_model() -> whisper.Whisper:
    _configure_ffmpeg()
    model_name = get_secret("WHISPER_MODEL", "base") or "base"
    LOGGER.info("Loading Whisper model: %s", model_name)
    return whisper.load_model(model_name)


def record_audio(
    filename: str = "temp_audio.wav",
    duration: int = DEFAULT_RECORD_SECONDS,
    sample_rate: int = SAMPLE_RATE,
) -> None:
    LOGGER.info("Recording %s seconds of audio...", duration)
    audio = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1)
    sd.wait()
    write(filename, sample_rate, audio)
    LOGGER.info("Recording saved to %s", filename)


def transcribe_audio(filename: str = "temp_audio.wav") -> str:
    if not Path(filename).is_file():
        raise FileNotFoundError(f"Audio file not found: {filename}")

    model = _get_whisper_model()
    result = model.transcribe(filename, fp16=False)
    text = result.get("text", "").strip()
    if not text:
        raise RuntimeError("Whisper returned empty transcription.")
    return text
