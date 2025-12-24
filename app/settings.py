from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    piper_voice_path: str
    audio_base_dir: str = "/mnt/audio"
    database_url: str
    redis_url: str

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )

settings = Settings()
