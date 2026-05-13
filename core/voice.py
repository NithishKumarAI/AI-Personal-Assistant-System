import os
import logging
from pathlib import Path
from groq import Groq
from scipy.io.wavfile import write
import sounddevice as sd
from core.config import get_secret

LOGGER = logging.getLogger(__name__)
RECORDING_SECONDS = 15
AUDIO_SAMPLE_RATE = 16000
TRANSCRIPTION_MODEL = "whisper-large-v3-turbo"
TRANSCRIPTION_TIMEOUT_SECONDS = 45
TRANSCRIPTION_FAILED_MESSAGE = "Transcription failed."

client = Groq(
    api_key=get_secret("GROQ_API_KEY")
)


def record_audio(filename="temp_audio.wav", duration=RECORDING_SECONDS, fs=AUDIO_SAMPLE_RATE):
    audio = sd.rec(
        int(duration * fs),
        samplerate=fs,
        channels=1,
    )
    sd.wait()
    write(filename, fs, audio)
    return filename


def transcribe_audio(filename="temp_audio.wav"):
    try:
        with Path(filename).open("rb") as audio_file:
            transcription = client.audio.transcriptions.create(
                file=audio_file,
                model=TRANSCRIPTION_MODEL,
                response_format="verbose_json",
                timeout=TRANSCRIPTION_TIMEOUT_SECONDS,
            )

        return transcription.text.strip()

    except Exception:
        LOGGER.warning("Groq transcription failed", exc_info=True)
        return TRANSCRIPTION_FAILED_MESSAGE
