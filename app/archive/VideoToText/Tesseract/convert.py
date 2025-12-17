import cv2
import pytesseract
from moviepy import VideoFileClip
import os

# مسیر tesseract (فقط در ویندوز)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def extract_subtitles_from_video(video_path, output_txt="subtitles_ocr.txt"):
    clip = VideoFileClip(video_path)
    fps = clip.fps
    duration = clip.duration
    subtitles = []
    prev_text = ""

    print("در حال استخراج زیرنویس از تصویر (OCR)...")

    for t in range(0, int(duration), 2):  # هر ۲ ثانیه یک فریم
        frame = clip.get_frame(t)
        h, w, _ = frame.shape

        # فقط پایین صفحه (محل زیرنویس)
        roi = frame[int(h*0.75):h, 0:w]

        # تبدیل به خاکستری + آستانه
        gray = cv2.cvtColor(roi, cv2.COLOR_RGB2GRAY)
        _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)

        # OCR
        text = pytesseract.image_to_string(thresh, lang='eng').strip()

        # فقط اگر تغییر کرد اضافه کن
        if text and text != prev_text and len(text) > 5:
            subtitles.append(f"[{t//60:02d}:{t%60:02d}] {text}")
            prev_text = text
            print(f"{t//60:02d}:{t%60:02d} → {text}")

    clip.close()

    # ذخیره
    with open(output_txt, "w", encoding="utf-8") as f:
        f.write("\n".join(subtitles))

    print(f"زیرنویس OCR در {output_txt} ذخیره شد.")
    return "\n".join(subtitles)

# اجرا
extract_subtitles_from_video("video.mp4")