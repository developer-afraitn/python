from pathlib import Path
from io import BytesIO

import numpy as np
import librosa
from piper import PiperVoice
from pydub import AudioSegment

from app.config import settings


class PiperWithoutSavingFileByFormat:
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

    def synthesize_ogg(
        self,
        text: str,
        select_lang: str = "fa",
        select_model_type: str = "",
        speed: float = 1.0,
        bitrate: str = "64k",
    ) -> bytes:
        if not text or not text.strip():
            raise ValueError("Text not provided")

        # speed clamp
        try:
            speed = float(speed)
        except Exception:
            speed = 1.0
        speed = min(max(speed, 0.5), 2.0)

        # language/model
        lang = "fa"
        lang_model = "fa_IR"
        model_type = "amir"  # پیش‌فرض فارسی

        if select_lang.lower() == "en":
            lang = "en"
            lang_model = "en_US"
            model_type = select_model_type or "hfc_female"
        else:
            # اگر خواستی برای فارسی هم انتخاب مدل بدهی:
            if select_model_type and select_model_type.strip():
                model_type = select_model_type.strip()

        model_path = self._resolve_model_path(lang, lang_model, model_type)
        voice = PiperVoice.load(str(model_path))

        # clean text
        text = (
            text.replace(".", "، ")
            .replace("؟", "")
            .replace("!", "")
            .strip()
        )
        if not text:
            raise ValueError("Text is empty after cleaning")

        # synthesize float audio
        chunks = voice.synthesize(text)
        audio = np.array([s for c in chunks for s in c.audio_float_array], dtype=np.float32)

        # time stretch (if enough samples)
        if speed != 1.0 and audio.size > 100:
            audio = librosa.effects.time_stretch(audio, rate=speed)

        # float32 [-1,1] -> int16 PCM
        audio_int16 = np.clip(audio, -1.0, 1.0)
        audio_int16 = (audio_int16 * 32767).astype(np.int16)

        # PCM bytes
        pcm_bytes = audio_int16.tobytes()

        # create AudioSegment from raw PCM
        segment = AudioSegment(
            data=pcm_bytes,
            sample_width=2,      # int16
            frame_rate=self.SAMPLE_RATE,
            channels=1,
        )

        # export OGG (needs ffmpeg)
        ogg_buffer = BytesIO()
        segment.export(
            ogg_buffer,
            format="ogg",
            bitrate=bitrate,
            codec="libvorbis",
        )
        return ogg_buffer.getvalue()
