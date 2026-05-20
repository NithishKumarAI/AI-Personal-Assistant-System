"""Local Whisper transcription and microphone capture."""

from __future__ import annotations

import logging
import os
import shutil
from pathlib import Path

import sounddevice as sd
import whisper
from scipy.io.wavfile import write

from core.config import get_secret

LOGGER = logging.getLogger(__name__)
DEFAULT_RECORD_SECONDS = 30
SAMPLE_RATE = 16000
FFMPEG_EXE = "ffmpeg.exe" if os.name == "nt" else "ffmpeg"


def _resolve_ffmpeg_bin_dir() -> Path | None:
    ffmpeg_path = get_secret("FFMPEG_PATH")
    if not ffmpeg_path:
        return None

    bin_dir = Path(ffmpeg_path.strip().strip('"')).expanduser()
    if bin_dir.is_file():
        return bin_dir.parent
    return bin_dir


def _configure_ffmpeg() -> None:
    bin_dir = _resolve_ffmpeg_bin_dir()
    if bin_dir is None:
        return

    if not bin_dir.is_dir():
        LOGGER.warning("FFMPEG_PATH is not a directory: %s", bin_dir)
        return

    resolved = str(bin_dir.resolve())
    if resolved not in os.environ.get("PATH", "").split(os.pathsep):
        os.environ["PATH"] = resolved + os.pathsep + os.environ.get("PATH", "")


def ffmpeg_executable() -> str | None:
    """Return the resolved ffmpeg binary path, if available."""
    _configure_ffmpeg()
    return shutil.which("ffmpeg")


def ensure_ffmpeg_ready() -> None:
    """Raise a clear error when ffmpeg is missing (Whisper needs it)."""
    _configure_ffmpeg()
    executable = ffmpeg_executable()
    if executable:
        LOGGER.debug("Using ffmpeg: %s", executable)
        return

    bin_dir = _resolve_ffmpeg_bin_dir()
    expected = (bin_dir / FFMPEG_EXE) if bin_dir else None
    if expected and expected.is_file():
        os.environ["PATH"] = str(expected.parent) + os.pathsep + os.environ.get("PATH", "")
        if shutil.which("ffmpeg"):
            return

    hint = (
        "ffmpeg was not found. Whisper needs ffmpeg to transcribe audio.\n"
        "Set FFMPEG_PATH in your .env file to the folder that contains ffmpeg.exe "
        "(for example, the `bin` folder inside your FFmpeg download)."
    )
    if bin_dir:
        hint += f"\nChecked FFMPEG_PATH: {bin_dir.resolve()}"
    raise RuntimeError(hint)


_configure_ffmpeg()
ensure_ffmpeg_ready()

WHISPER_MODEL_NAME = get_secret("WHISPER_MODEL", "base") or "base"
LOGGER.info("Loading Whisper model: %s", WHISPER_MODEL_NAME)
WHISPER_MODEL = whisper.load_model(WHISPER_MODEL_NAME)


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

    ensure_ffmpeg_ready()
    result = WHISPER_MODEL.transcribe(filename, fp16=False)
    text = result.get("text", "").strip()
    if not text:
        raise RuntimeError("Whisper returned empty transcription.")
    return text
