from moviepy import VideoFileClip
from pydub import AudioSegment
import speech_recognition as sr
import os

def video_to_text(video_path, output_text_file=None):
    # 1. استخراج صدا از ویدئو
    print("در حال استخراج صدا از ویدئو...")
    video = VideoFileClip(video_path)
    audio_path = "temp_audio.wav"
    video.audio.write_audiofile(audio_path)

    # 2. تبدیل به فرمت مناسب (WAV, mono, 16kHz)
    print("در حال پردازش فایل صوتی...")
    audio = AudioSegment.from_wav(audio_path)
    audio = audio.set_channels(1)  # مونو
    audio = audio.set_frame_rate(16000)  # 16kHz
    processed_audio_path = "processed_audio.wav"
    audio.export(processed_audio_path, format="wav")

    # 3. تشخیص گفتار با pocketsphinx (آفلاین)
    print("در حال تبدیل گفتار به متن...")
    recognizer = sr.Recognizer()
    with sr.AudioFile(processed_audio_path) as source:
        audio_data = recognizer.record(source)

    try:
        # text = recognizer.recognize_sphinx(audio_data, language="fa-IR")  # برای فارسی
        text = recognizer.recognize_sphinx(audio_data, language="en-US")  # برای انگلیسی
    except sr.UnknownValueError:
        text = "هیچ گفتاری تشخیص داده نشد."
    except sr.RequestError as e:
        text = f"خطا در تشخیص: {e}"

    # 4. ذخیره متن (اختیاری)
    if output_text_file:
        with open(output_text_file, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"متن در {output_text_file} ذخیره شد.")

    # 5. پاکسازی فایل‌های موقت
    if os.path.exists(audio_path):
        os.remove(audio_path)
    if os.path.exists(processed_audio_path):
        os.remove(processed_audio_path)

    return text

# استفاده
video_file = "video.mp4"  # مسیر ویدئو
result = video_to_text(video_file, "output.txt")
print("\nمتن استخراج شده:\n", result)