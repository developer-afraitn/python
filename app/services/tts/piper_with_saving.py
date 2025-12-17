from pathlib import Path
import wave
import numpy as np
from piper import PiperVoice

from app.config import settings


class PiperTTSFileService:
    SAMPLE_RATE = 22050

    def __init__(self):
        self.base_path = Path(settings.piper_voice_path)

    def _resolve_model_path(self, lang: str, lang_model: str, model_type: str) -> Path:
        model_path = (
            self.base_path
            / lang
            / lang_model
            / model_type
            / "medium"
            / f"{lang_model}-{model_type}-medium.onnx"
        )

        if not model_path.exists():
            raise FileNotFoundError(f"Model not found: {model_path}")

        return model_path

    def synthesize_to_file(
        self,
        text: str,
        model_type: str,
        out_dir: str = "outputs",
        lang: str = "fa",
        lang_model: str = "fa_IR",
    ) -> str:
        if not text.strip():
            raise ValueError("Text not provided")

        # پاکسازی متن مثل کد خودت
        text = (
            text.replace("...", " ")
            .replace(".", "، ")
            .replace("؟", " ")
            .replace("!", " ")
        )

        model_path = self._resolve_model_path(lang, lang_model, model_type)

        voice = PiperVoice.load(str(model_path))
        chunks = voice.synthesize(text)

        audio_samples = [s for c in chunks for s in c.audio_float_array]
        audio = np.array(audio_samples, dtype=np.float32)

        out_path = Path(out_dir)
        out_path.mkdir(parents=True, exist_ok=True)

        filename = f"{model_type}.wav"
        file_path = out_path / filename

        with wave.open(str(file_path), "wb") as f:
            f.setnchannels(1)
            f.setsampwidth(2)
            f.setframerate(self.SAMPLE_RATE)
            f.writeframes(np.int16(audio * 32767).tobytes())

        return str(file_path)
