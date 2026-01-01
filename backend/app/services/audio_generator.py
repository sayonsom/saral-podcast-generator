"""ElevenLabs TTS service for podcast audio generation."""
import re
from dataclasses import dataclass

from app.config import settings

# Placeholder - install: pip install elevenlabs
# from elevenlabs import ElevenLabs, VoiceSettings


@dataclass
class AudioSegment:
    speaker: str
    text: str
    voice_id: str
    audio_path: str | None = None
    duration_ms: int = 0


class AudioGenerator:
    """Generate speech from script using ElevenLabs API."""

    def __init__(self):
        # self.client = ElevenLabs(api_key=settings.elevenlabs_api_key)
        self.voices = {
            "doug": settings.elevenlabs_doug_voice_id,
            "claire": settings.elevenlabs_claire_voice_id,
        }
        # Balanced settings for natural podcast speech
        self.voice_settings = {
            "stability": 0.5,
            "similarity_boost": 0.75,
            "style": 0.0,
            "use_speaker_boost": True
        }

    def parse_script(self, script: str) -> list[dict]:
        """
        Parse script into speaker segments.
        
        Handles format:
        DOUG: Some dialogue here [laughs] more text.
        CLAIRE: Response text [sighs] etc.
        """
        segments = []
        
        # Match SPEAKER: content until next speaker or end
        pattern = r'(DOUG|CLAIRE):\s*(.+?)(?=(?:\n(?:DOUG|CLAIRE):)|$)'
        
        for match in re.finditer(pattern, script, re.DOTALL | re.IGNORECASE):
            speaker = match.group(1).lower()
            text = match.group(2).strip()
            
            # Remove stage directions [laughs], [sighs], [00:00], etc.
            text = re.sub(r'\[.*?\]', '', text)
            # Clean up extra whitespace
            text = ' '.join(text.split())
            
            if text:
                segments.append({
                    "speaker": speaker,
                    "text": text,
                    "voice_id": self.voices[speaker]
                })
        
        return segments

    async def generate_segment(self, speaker: str, text: str) -> bytes:
        """Generate audio for a single segment via ElevenLabs."""
        voice_id = self.voices[speaker]
        
        # TODO: Uncomment when elevenlabs installed
        # audio = await self.client.text_to_speech.convert(
        #     voice_id=voice_id,
        #     text=text,
        #     model_id="eleven_multilingual_v2",
        #     voice_settings=VoiceSettings(**self.voice_settings)
        # )
        # return audio
        
        # Placeholder
        raise NotImplementedError("Install elevenlabs and configure API key")

    async def generate_full_episode(
        self,
        script: str,
        episode_id: str
    ) -> list[AudioSegment]:
        """
        Generate all audio segments for an episode.
        
        Returns list of AudioSegment with paths to generated audio files.
        """
        from app.services.storage import storage
        
        segments = self.parse_script(script)
        results = []
        
        for i, seg in enumerate(segments):
            # Generate audio
            audio_bytes = await self.generate_segment(seg["speaker"], seg["text"])
            
            # Upload to storage
            path = f"episodes/{episode_id}/segments/segment_{i:03d}.mp3"
            audio_url = await storage.upload_audio(audio_bytes, path)
            
            results.append(AudioSegment(
                speaker=seg["speaker"],
                text=seg["text"],
                voice_id=seg["voice_id"],
                audio_path=audio_url
            ))
        
        return results

    def estimate_duration(self, text: str) -> int:
        """Estimate speech duration in milliseconds (rough: 150 wpm)."""
        words = len(text.split())
        minutes = words / 150
        return int(minutes * 60 * 1000)
