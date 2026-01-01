"""Application configuration."""
import os
from pathlib import Path
from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

# Load .env file explicitly - this sets env vars if not already set with value
_env_file = Path(__file__).parent.parent.parent / ".env"
if _env_file.exists():
    # Read .env values and set them in environment (override empty values)
    from dotenv import dotenv_values
    _env_values = dotenv_values(_env_file)
    for key, value in _env_values.items():
        if value:  # Only set if value is not empty
            os.environ[key] = value


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        extra="ignore"
    )

    # AI
    anthropic_api_key: str = ""
    anthropic_model: str = "claude-sonnet-4-20250514"

    # Audio (ElevenLabs)
    elevenlabs_api_key: str = ""
    elevenlabs_doug_voice_id: str = "pNInz6obpgDQGcFmaJgB"  # Adam
    elevenlabs_claire_voice_id: str = "EXAVITQu4vr4xnSDxMaL"  # Rachel

    # Images
    unsplash_access_key: str = ""

    # Spotify
    spotify_client_id: str = ""
    spotify_client_secret: str = ""
    spotify_redirect_uri: str = "http://localhost:3000/api/spotify/callback"
    spotify_show_id: str = ""

    # GCP
    gcp_project_id: str = ""
    gcs_bucket: str = "podcast-generator-assets"
    firestore_collection: str = "podcast_generator"

    # Server
    cors_origins: list[str] = ["http://localhost:3000"]


settings = Settings()
