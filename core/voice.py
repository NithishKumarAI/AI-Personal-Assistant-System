import whisper
import sounddevice as sd
from scipy.io.wavfile import write
import os

os.environ["PATH"] += os.pathsep + r"C:\Users\nithi\Downloads\ffmpeg-8.1-essentials_build\ffmpeg-8.1-essentials_build\bin"
model = whisper.load_model("base")

def record_audio(filename="temp_audio.wav", duration=30, fs=16000):
    print("recording...")
    audio = sd.rec(int(duration*fs), samplerate=fs, channels=1)
    sd.wait()
    write(filename,fs,audio)
    print("done")

def transcribe_audio(filename="input.wav"):
    result = model.transcribe(filename,fp16=False)
    return result['text']