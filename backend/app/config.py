"""Application configuration."""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
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
    
    class Config:
        env_file = ".env"


settings = Settings()
