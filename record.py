import queue
import time
import numpy as np
import sounddevice as sd
from settings import SAMPLE_RATE, BLOCK_SIZE, SILENCE_THRESHOLD, SILENCE_SECONDS, MAX_SECONDS

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