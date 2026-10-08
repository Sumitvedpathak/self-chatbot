# ---------- Settings ----------
MODEL_SIZE = "small"       # tiny / base / small / medium / large-v3
LANGUAGE = "en"            # None = auto-detect; or "hi", "mr", "fr", ...
SAMPLE_RATE = 16000        # Whisper expects 16 kHz
BLOCK_SIZE = 1024          # ~64 ms of audio per block
SILENCE_THRESHOLD = 0.01   # raise if it never stops, lower if it cuts you off
SILENCE_SECONDS = 1.2      # how long a pause counts as "done talking"
MAX_SECONDS = 30           # safety limit per recording
# ---------- Load model once (first run downloads it) ----------