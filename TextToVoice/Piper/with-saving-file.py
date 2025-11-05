
from piper import PiperVoice
import wave
import numpy as np
import os
import sys
sys.stdout.reconfigure(encoding='utf-8')

# مسیر مدل

model_type="amir"
model_type1="ganji"
model_type1="ganji_adabi"
model_type1="gyro"
model_type1="reza_ibrahim"

model_path = rf"D:\work\python\piper-voices\fa\fa_IR\{model_type}\medium\fa_IR-{model_type}-medium.onnx"  # مرد
# model_path = r"C:\piper_models\fa_IR-gyro-medium.onnx"  # زن

if not os.path.exists(model_path):
    print(f"خطا: فایل پیدا نشد! {model_path}")
    exit()

print("در حال بارگذاری مدل...")
voice = PiperVoice.load(model_path)
# --- متن از آرگومان ---
if len(sys.argv) < 2:
    text = "سلام! این تست   است."
else:
    text = sys.argv[1]

text = text.replace(".", "، ")   # نقطه → ویرگول فارسی (مکث طبیعی)
text = text.replace("؟", " ")       # علامت سؤال → فاصله
text = text.replace("!", " ")       # تعجب → فاصله
text = text.replace("...", " ")     # سه نقطه → فاصله
chunks = list(voice.synthesize(text))

# جمع کردن همه نمونه‌های صوتی (float32)
audio_samples = []
for chunk in chunks:
    audio_samples.extend(chunk.audio_float_array)  # فیلد درست!

# تبدیل به آرایه numpy
audio = np.array(audio_samples, dtype=np.float32)

# ذخیره به WAV
filename = "final_persian_voice.wav"
with wave.open(filename, "wb") as f:
    f.setnchannels(1)
    f.setsampwidth(2)
    f.setframerate(22050)
    f.writeframes(np.int16(audio * 32767).tobytes())

print(f"موفقیت! فایل ساخته شد: {filename}")