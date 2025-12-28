from pathlib import Path
import speech_recognition as sr
from app.settings import settings

class GoogleSTTService:
    def transcribe_under_base(self, rel_path: str, lang: str = "fa") -> dict:
        base = Path(settings.audio_base_dir).resolve()
        target = (base / rel_path).resolve()

        # جلوگیری از دسترسی به بیرون فولدر mount شده
        if base not in target.parents and target != base:
            return {
                "error": "مسیر غیرمجاز است",
                "base": str(base),
                "target": str(target)
            }

        if not target.exists():
            return {
                "error": "فایل پیدا نشد",
                "base": str(base),
                "target": str(target)
            }

        language = "fa-IR" if lang != "en" else "en-US"

        r = sr.Recognizer()
        with sr.AudioFile(str(target)) as source:
            audio = r.record(source)

        try:
            text = r.recognize_google(audio, language=language)
            return {"text": text}
        except sr.UnknownValueError:
            return {"error": "صدا تشخیص داده نشد"}
        except sr.RequestError as e:
            return {"error": f"خطا در اتصال به گوگل: {e}"}
