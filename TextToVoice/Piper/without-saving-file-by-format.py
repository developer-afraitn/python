# tts_stream.py - تبدیل متن به صدا با Piper + خروجی OGG + سرعت 0.5x–2.0x

import sys
import os
import numpy as np
from io import BytesIO
from piper import PiperVoice
from dotenv import load_dotenv
import librosa
from pydub import AudioSegment

# --- تنظیم انکودینگ ---
sys.stdout.reconfigure(encoding='utf-8')

# --- لود .env ---
def load_root_env():
    current = os.path.dirname(os.path.abspath(__file__))
    while True:
        env_path = os.path.join(current, '.env')
        if os.path.exists(env_path):
            load_dotenv(env_path)
            return
        parent = os.path.dirname(current)
        if parent == current:
            raise FileNotFoundError("فایل .env پیدا نشد!")
        current = parent

load_root_env()
PIPER_VOICE_PATH = os.getenv("PIPER_VOICE_PATH")
if not PIPER_VOICE_PATH:
    print("خطا: PIPER_VOICE_PATH در .env تنظیم نشده!", file=sys.stderr)
    sys.exit(1)

# --- ورودی‌ها ---
if len(sys.argv) < 2:
    print("استفاده: python tts_stream.py \"متن\" [lang] [model] [speed]", file=sys.stderr)
    sys.exit(1)

text = sys.argv[1]
select_lang = sys.argv[2].lower() if len(sys.argv) > 2 else "fa"
select_model_type = sys.argv[3] if len(sys.argv) > 3 else ""
speed_str = sys.argv[4] if len(sys.argv) > 4 else "1.0"

# --- تبدیل سرعت ---
try:
    speed = float(speed_str)
    if not (0.5 <= speed <= 2.0):
        speed = 1.0
except:
    speed = 1.0

# --- تنظیم زبان و مدل ---
lang = 'fa'
lang_model = 'fa_IR'
model_type = "amir"

if select_lang == 'en':
    lang = 'en'
    lang_model = 'en_US'
    model_type = select_model_type or 'hfc_female'

MODEL_PATH = f"{PIPER_VOICE_PATH}/{lang}/{lang_model}/{model_type}/medium/{lang_model}-{model_type}-medium.onnx"

# --- چک مدل ---
if not os.path.exists(MODEL_PATH):
    print(f"مدل پیدا نشد: {MODEL_PATH}", file=sys.stderr)
    sys.exit(1)

# --- بارگذاری مدل ---
voice = PiperVoice.load(MODEL_PATH)

# --- تمیز کردن متن ---
text = text.replace(".", "، ").replace("؟", "").replace("!", "").strip()
if not text:
    print("متن خالی!", file=sys.stderr)
    sys.exit(1)

# --- تولید صدا ---
chunks = list(voice.synthesize(text))
audio = np.array([s for c in chunks for s in c.audio_float_array], dtype=np.float32)

# --- تغییر سرعت ---
if speed != 1.0 and len(audio) > 100:
    audio = librosa.effects.time_stretch(audio, rate=speed)

# --- تبدیل به AudioSegment ---
audio_int16 = (audio * 32767).astype(np.int16)
byte_io = BytesIO()
np.save(byte_io, audio_int16)
byte_io.seek(0)

audio_segment = AudioSegment(
    data=byte_io.read(),
    frame_rate=22050,
    sample_width=2,
    channels=1
)

# --- خروجی OGG به stdout ---
ogg_buffer = BytesIO()
# bitrate: 32k تا 128k (کیفیت بالا)
audio_segment.export(ogg_buffer, format="ogg", bitrate="64k", codec="libvorbis")
sys.stdout.buffer.write(ogg_buffer.getvalue())