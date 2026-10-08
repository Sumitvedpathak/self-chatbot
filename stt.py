import time
import os
from dotenv import load_dotenv
import win32com.client
from faster_whisper import WhisperModel
from settings import MODEL_SIZE, SAMPLE_RATE, BLOCK_SIZE, SILENCE_THRESHOLD, SILENCE_SECONDS, MAX_SECONDS, LANGUAGE
from llm import call_llm
from record import record_until_silence



print("Loading speech model...")
model = WhisperModel(MODEL_SIZE, device="cpu", compute_type="int8")
tts_speaker = win32com.client.Dispatch("SAPI.SpVoice")


def speak(text):
    """Speak text locally through the computer's default audio output."""
    text = text.strip()
    if not text:
        print("No assistant text to speak.")
        return

    try:
        tts_speaker.Speak(text)
    except Exception as error:
        print(f"Text-to-speech failed: {error}")





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
            try:
                response_text = call_llm(text)
                if not isinstance(response_text, str):
                    response_text = " ".join(
                        block["text"] for block in response_text
                        if isinstance(block, dict) and isinstance(block.get("text"), str)
                    )
                print(f"Assistant: {response_text}")
                print("Speaking response...")
                speak(response_text)
            except Exception as error:
                print(f"LLM request failed: {error}")
            print(f"({time.time() - start:.1f}s)\n")
    except KeyboardInterrupt:
        print("\nBye!")