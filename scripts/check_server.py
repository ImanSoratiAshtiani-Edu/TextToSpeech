"""Generate and validate a short WAV without playing it."""
import io
from pathlib import Path
import sys
import wave

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from main import MODEL, client

with client.audio.speech.with_streaming_response.create(
    model=MODEL, voice="ryan", input="Hello. The Kaspar speech demo is ready.", response_format="wav"
) as response:
    data = response.read()
with wave.open(io.BytesIO(data), "rb") as wav:
    frames = wav.readframes(wav.getnframes())
    if not frames or wav.getframerate() <= 0:
        raise RuntimeError("Server returned empty or invalid audio")
    print(f"PASS: WAV received; rate={wav.getframerate()}, channels={wav.getnchannels()}, audio_bytes={len(frames)}")
