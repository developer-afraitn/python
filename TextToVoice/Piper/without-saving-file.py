# tts_stream.py - با تنظیم سرعت صدا (0.5x تا 2.0x)

import sys
import wave
import numpy as np
from io import BytesIO
from piper import PiperVoice
import os
from dotenv import load_dotenv
import librosa  # <-- اضافه شد

sys.stdout.reconfigure(encoding='utf-8')

# --- لود .env از روت پروژه ---
def load_root_env():
    current = os.path.dirname(os.path.abspath(__file__))
    while True:
        env_path = os.path.join(current, '.env')
        if os.path.exists(env_path):
            load_dotenv(env_path)
            return
        parent = os.path.dirname(current)
        if parent == current:
            raise FileNotFoundError("فایل .env در روت پروژه پیدا نشد!")
        current = parent

load_root_env()
PIPER_VOICE_PATH = os.getenv("PIPER_VOICE_PATH")

# --- ورودی‌ها ---
text = sys.argv[1] if len(sys.argv) > 1 else ""
select_lang = sys.argv[2] if len(sys.argv) > 2 else ""
select_model_type = sys.argv[3] if len(sys.argv) > 3 else ""
#speed_str = sys.argv[3] if len(sys.argv) > 3 else "1.0"  # سرعت پیش‌فرض 1.0x
speed_str="1.0"
# --- تبدیل سرعت به float ---
try:
    speed = float(speed_str)
    if not 0.5 <= speed <= 2.0:
        speed = 1.0  # محدود کردن
except:
    speed = 1.0

# --- انتخاب زبان و مدل ---
lang = 'fa'
lang_model = 'fa_IR'
model_type = "amir"

match select_lang:
    case 'en':
        lang = 'en'
        lang_model = 'en_US'
        if select_model_type.strip():
            model_type = select_model_type
        else:
            model_type = 'hfc_female'

#MODEL_PATH = rf"{PIPER_VOICE_PATH}\{lang}\{lang_model}\{model_type}\medium\{lang_model}-{model_type}-medium.onnx"
MODEL_PATH = rf"{PIPER_VOICE_PATH}/{lang}/{lang_model}/{model_type}/medium/{lang_model}-{model_type}-medium.onnx"

# --- چک مدل ---
if not os.path.exists(MODEL_PATH):
    print(f"Model not found: {MODEL_PATH}", file=sys.stderr)
    sys.exit(1)

# --- بارگذاری مدل ---
voice = PiperVoice.load(MODEL_PATH)

# --- چک متن ---
if not text.strip():
    print("Text not provided", file=sys.stderr)
    sys.exit(1)


text = text.replace(".", "، ").replace("؟", "").replace("!", "")

# --- تولید صدا ---
chunks = list(voice.synthesize(text))
audio_samples = [sample for chunk in chunks for sample in chunk.audio_float_array]
audio = np.array(audio_samples, dtype=np.float32)

# --- تغییر سرعت (time stretch) ---
if speed != 1.0:
    audio = librosa.effects.time_stretch(audio, rate=speed)
    # نرخ نمونه جدید
    SAMPLE_RATE = int(22050 * speed)
else:
    SAMPLE_RATE = 22050

# --- تبدیل به WAV در حافظه ---
buffer = BytesIO()
with wave.open(buffer, "wb") as wav_file:
    wav_file.setnchannels(1)
    wav_file.setsampwidth(2)
    wav_file.setframerate(SAMPLE_RATE)
    wav_file.writeframes(np.int16(audio * 32767).tobytes())

# --- خروجی به stdout (بایت) ---
sys.stdout.buffer.write(buffer.getvalue())