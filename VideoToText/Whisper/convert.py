# video_to_text.py
from moviepy import VideoFileClip
import whisper
import os

def video_to_text(video_path="video.mp4", model_name="base"):
    print("در حال بارگذاری مدل Whisper...")
    model = whisper.load_model(model_name)  # base = سریع و دقیق برای انگلیسی

    print("در حال استخراج صدا از ویدئو...")
    clip = VideoFileClip(video_path)
    audio_path = "temp_audio.wav"
    clip.audio.write_audiofile(audio_path)
    clip.close()

    print("در حال تبدیل صدا به متن (انگلیسی)...")
    result = model.transcribe(audio_path, language="en")
    text = result["text"].strip()

    # پاکسازی
    if os.path.exists(audio_path):
        os.remove(audio_path)

    # ذخیره متن کامل
    with open("full_text.txt", "w", encoding="utf-8") as f:
        f.write(text)

    # ذخیره با زمان‌بندی (مثل زیرنویس)
    with open("transcript_with_time.txt", "w", encoding="utf-8") as f:
        for seg in result["segments"]:
            start = seg["start"]
            end = seg["end"]
            txt = seg["text"].strip()
            f.write(f"[{start:.2f} --> {end:.2f}] {txt}\n")

    print("متن کامل در full_text.txt ذخیره شد.")
    print("زیرنویس با زمان در transcript_with_time.txt ذخیره شد.")
    return text

# اجرا
if __name__ == "__main__":
    text = video_to_text("D:\learning\english\EmmaDailyEnglish\Master ENGLISH Past Tenses with a Touching Story _ Easy Listening Practice (A2 Level) (1).mp4", model_name="small")  # small = دقت بالاتر
    print("\n--- نمونه متن (500 کاراکتر اول) ---")
    print(text)