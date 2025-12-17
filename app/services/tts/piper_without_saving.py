import os
import wave
import numpy as np
from io import BytesIO
import librosa
from piper import PiperVoice
from pathlib import Path

from app.config import settings


class PiperTTSService:
    SAMPLE_RATE = 22050

    def __init__(self):
        self.base_path = settings.piper_voice_path

    def _resolve_model_path(
        self,
        lang: str,
        lang_model: str,
        model_type: str,
    ) -> str:
        model_path = Path(self.base_path) / lang / lang_model / model_type / "medium" / f"{lang_model}-{model_type}-medium.onnx"

        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model not found: {model_path}")

        return model_path

    def synthesize(
        self,
        text: str,
        select_lang: str = "fa",
        select_model_type: str = "",
        speed: float = 1.0,
    ) -> bytes:
        if not text.strip():
            raise ValueError("Text not provided")

        # ---------- language ----------
        lang = "fa"
        lang_model = "fa_IR"
        model_type = "amir"

        if select_lang == "en":
            lang = "en"
            lang_model = "en_US"
            model_type = select_model_type or "hfc_female"

        speed = min(max(speed, 0.5), 2.0)

        model_path = self._resolve_model_path(lang, lang_model, model_type)
        voice = PiperVoice.load(model_path)

        text = (
            text.replace(".", "، ")
            .replace("؟", "")
            .replace("!", "")
        )

        chunks = voice.synthesize(text)
        audio_samples = [
            sample
            for chunk in chunks
            for sample in chunk.audio_float_array
        ]

        audio = np.array(audio_samples, dtype=np.float32)

        sample_rate = self.SAMPLE_RATE
        if speed != 1.0:
            audio = librosa.effects.time_stretch(audio, rate=speed)
            sample_rate = int(self.SAMPLE_RATE * speed)

        buffer = BytesIO()
        with wave.open(buffer, "wb") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(
                np.int16(audio * 32767).tobytes()
            )

        return buffer.getvalue()
