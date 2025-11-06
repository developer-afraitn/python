import sys
import speech_recognition as sr
import json

def main():

    audio_path = sys.argv[1] if len(sys.argv) > 1 else ""
    if not audio_path.strip():
        print(json.dumps({"error": "مسیر فایل لازم است."}))
        sys.exit(1)


    lang = 'fa-IR'
    select_lang = sys.argv[2] if len(sys.argv) > 2 else ""

    match select_lang:
        case 'en': lang = 'en-US'
        case 'fa': lang = 'fa-IR'


    audio_path = sys.argv[1]

    # چک کردن وجود فایل
    import os
    if not os.path.exists(audio_path):
        print(json.dumps({"error": "فایل پیدا نشد."}))
        return

    r = sr.Recognizer()
    try:
        with sr.AudioFile(audio_path) as source:
            audio = r.record(source)
        text = r.recognize_google(audio, language=lang)
        print(json.dumps({"text": text}))
    except sr.UnknownValueError:
        print(json.dumps({"error": "صدا قابل تشخیص نبود."}))
    except sr.RequestError as e:
        print(json.dumps({"error": f"خطا در اتصال: {e}"}))
    except Exception as e:
        print(json.dumps({"error": f"خطای غیرمنتظره: {e}"}))

if __name__ == "__main__":
    main()