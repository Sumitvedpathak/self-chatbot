import queue
import time

import numpy as np
import sounddevice as sd
from faster_whisper import WhisperModel

# ---------- Settings ----------
MODEL_SIZE = "small"       # tiny / base / small / medium / large-v3
LANGUAGE = "en"            # None = auto-detect; or "hi", "mr", "fr", ...
SAMPLE_RATE = 16000        # Whisper expects 16 kHz
BLOCK_SIZE = 1024          # ~64 ms of audio per block
SILENCE_THRESHOLD = 0.01   # raise if it never stops, lower if it cuts you off
SILENCE_SECONDS = 1.2      # how long a pause counts as "done talking"
MAX_SECONDS = 30           # safety limit per recording

# ---------- Load model once (first run downloads it) ----------
print("Loading speech model...")
model = WhisperModel(MODEL_SIZE, device="cpu", compute_type="int8")


def record_until_silence():
    """Record from the mic. Starts counting silence only after you begin speaking."""
    q = queue.Queue()

    def callback(indata, frames, time_info, status):
        if status:
            print(status)
        q.put(indata.copy())

    chunks = []
    started = False
    silent_for = 0.0
    t0 = time.time()

    with sd.InputStream(samplerate=SAMPLE_RATE, channels=1, dtype="float32",
                        blocksize=BLOCK_SIZE, callback=callback):
        while time.time() - t0 < MAX_SECONDS:
            block = q.get()
            chunks.append(block)
            rms = float(np.sqrt(np.mean(block ** 2)))  # loudness of this block

            if rms > SILENCE_THRESHOLD:
                started = True
                silent_for = 0.0
            elif started:
                silent_for += len(block) / SAMPLE_RATE
                if silent_for >= SILENCE_SECONDS:
                    break

    if not started:
        return None  # nothing but silence
    return np.concatenate(chunks).flatten()


def transcribe(audio):
    """audio: float32 numpy array at 16 kHz (or a path to an audio file)."""
    segments, info = model.transcribe(
        audio,
        language=LANGUAGE,
        beam_size=5,
        vad_filter=True,   # skips non-speech, reduces Whisper "hallucinations"
    )
    # `segments` is a generator; the actual work happens as we iterate
    return " ".join(seg.text.strip() for seg in segments).strip()


if __name__ == "__main__":
    print("Ready. Press Ctrl+C to quit.\n")
    try:
        while True:
            input("Press Enter, then speak...")
            print("Listening...")
            audio = record_until_silence()
            if audio is None:
                print("I didn't hear anything. Try again.\n")
                continue

            print("Transcribing...")
            start = time.time()
            text = transcribe(audio)
            print(f"You said: {text}")
            print(f"({time.time() - start:.1f}s)\n")
    except KeyboardInterrupt:
        print("\nBye!")