# tts_stream.py - بدون ذخیره فایل، خروجی به stdout

import sys
import wave
import numpy as np
from io import BytesIO
from piper import PiperVoice
sys.stdout.reconfigure(encoding='utf-8')

# --- تنظیمات ---
model_type="amir"
model_type1="ganji"
model_type1="ganji_adabi"
model_type1="gyro"
model_type1="reza_ibrahim"

MODEL_PATH = rf"D:\work\python\piper-voices\fa\fa_IR\{model_type}\medium\fa_IR-{model_type}-medium.onnx"  # مرد

SAMPLE_RATE = 22050

# --- چک مدل ---
if not __import__('os').path.exists(MODEL_PATH):
    print(f"Model not found: {MODEL_PATH}", file=sys.stderr)
    sys.exit(1)

# --- بارگذاری مدل ---
voice = PiperVoice.load(MODEL_PATH)

# --- متن ---
text = sys.argv[1] if len(sys.argv) > 1 else "سلام! این تست است."
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