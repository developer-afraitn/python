# tts_stream.py - بدون ذخیره فایل، خروجی به stdout

import sys
import wave
import numpy as np
from io import BytesIO
from piper import PiperVoice
import os
from dotenv import load_dotenv
sys.stdout.reconfigure(encoding='utf-8')

def load_root_env():
    current = os.path.dirname(os.path.abspath(__file__))
    while True:
        if os.path.exists(os.path.join(current, '.env')):
            load_dotenv(os.path.join(current, '.env'))
            return
        parent = os.path.dirname(current)
        if parent == current:
            raise FileNotFoundError("فایل .env در روت پروژه پیدا نشد!")
        current = parent

load_root_env()  # فقط یک بار
PIPER_VOICE_PATH = os.getenv("PIPER_VOICE_PATH")


lang = 'fa'
lang_model = 'fa_IR'
model_type="amir"

select_lang = sys.argv[2] if len(sys.argv) > 2 else ""

match select_lang:
    case 'en':
        lang = 'en'
        lang_model = 'en_US'
        model_type="hfc_female"
MODEL_TYPE = os.getenv("MODEL_TYPE")

MODEL_PATH = rf"{PIPER_VOICE_PATH}\{lang}\{lang_model}\{model_type}\medium\{lang_model}-{model_type}-medium.onnx"  # مرد

SAMPLE_RATE = 22050


# --- چک مدل ---
if not __import__('os').path.exists(MODEL_PATH):
    print(f"Model not found: {MODEL_PATH}", file=sys.stderr)
    sys.exit(1)

# --- بارگذاری مدل ---
voice = PiperVoice.load(MODEL_PATH)

# --- متن ---
text = sys.argv[1] if len(sys.argv) > 1 else ""


if not text:
    print(f"text not found", file=sys.stderr)
    sys.exit(1)


text = text.replace(".", "، ").replace("؟", "").replace("!", "")

# --- تولید صدا ---
chunks = list(voice.synthesize(text))
audio_samples = [sample for chunk in chunks for sample in chunk.audio_float_array]
audio = np.array(audio_samples, dtype=np.float32)

# --- تبدیل به بایت WAV در حافظه ---
buffer = BytesIO()
with wave.open(buffer, "wb") as wav_file:
    wav_file.setnchannels(1)
    wav_file.setsampwidth(2)
    wav_file.setframerate(SAMPLE_RATE)
    wav_file.writeframes(np.int16(audio * 32767).tobytes())

# --- خروجی به stdout (بایت) ---
sys.stdout.buffer.write(buffer.getvalue())