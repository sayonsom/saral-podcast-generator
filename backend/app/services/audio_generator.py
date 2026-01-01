"""ElevenLabs TTS service for podcast audio generation."""
import re
import os
import tempfile
from pathlib import Path
from dataclasses import dataclass, field

from elevenlabs import ElevenLabs, VoiceSettings

from app.config import settings


@dataclass
class AudioSegment:
    """Represents a generated audio segment."""
    speaker: str
    text: str
    voice_id: str
    audio_path: str | None = None
    duration_ms: int = 0


class AudioGenerator:
    """Generate speech from script using ElevenLabs API."""

    def __init__(self):
        if not settings.elevenlabs_api_key:
            raise ValueError("ELEVENLABS_API_KEY not configured")

        self.client = ElevenLabs(api_key=settings.elevenlabs_api_key)
        self.voices = {
            "doug": settings.elevenlabs_doug_voice_id,
            "claire": settings.elevenlabs_claire_voice_id,
        }
        # Balanced settings for natural podcast speech
        self.voice_settings = VoiceSettings(
            stability=0.5,
            similarity_boost=0.75,
            style=0.0,
            use_speaker_boost=True
        )

    def parse_script(self, script: str) -> list[dict]:
        """
        Parse script into speaker segments.

        Handles formats:
        - DOUG: Some dialogue here [laughs] more text.
        - **DOUG:** Bold markdown format
        - CLAIRE: Response text [sighs] etc.
        """
        segments = []

        # Match SPEAKER: or **SPEAKER:** content until next speaker or end
        # More robust pattern that handles various markdown formats
        pattern = r'\*{0,2}(DOUG|CLAIRE)\*{0,2}:\s*(.+?)(?=\n\s*\*{0,2}(?:DOUG|CLAIRE)\*{0,2}:|$)'

        for match in re.finditer(pattern, script, re.DOTALL | re.IGNORECASE):
            speaker = match.group(1).lower()
            text = match.group(2).strip()

            # Remove stage directions [laughs], [sighs], [00:00], etc.
            text = re.sub(r'\[.*?\]', '', text)
            # Remove markdown formatting
            text = re.sub(r'\*+', '', text)
            # Clean up extra whitespace
            text = ' '.join(text.split())

            if text and len(text) > 5:  # Skip very short segments
                segments.append({
                    "speaker": speaker,
                    "text": text,
                    "voice_id": self.voices[speaker]
                })

        return segments

    def generate_segment_sync(self, speaker: str, text: str) -> bytes:
        """Generate audio for a single segment via ElevenLabs (synchronous)."""
        voice_id = self.voices[speaker]

        # Use the synchronous generate method
        audio_generator = self.client.text_to_speech.convert(
            voice_id=voice_id,
            text=text,
            model_id="eleven_multilingual_v2",
            voice_settings=self.voice_settings
        )

        # Collect all chunks into bytes
        audio_bytes = b''.join(chunk for chunk in audio_generator)
        return audio_bytes

    async def generate_segment(self, speaker: str, text: str) -> bytes:
        """Generate audio for a single segment via ElevenLabs."""
        import asyncio
        # Run synchronous API call in thread pool
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self.generate_segment_sync,
            speaker,
            text
        )

    async def generate_full_episode(
        self,
        script: str,
        episode_id: str,
        output_dir: Path | None = None
    ) -> list[AudioSegment]:
        """
        Generate all audio segments for an episode.

        Args:
            script: The podcast script text
            episode_id: Unique episode identifier
            output_dir: Local directory to save files (optional, uses temp if not provided)

        Returns:
            List of AudioSegment with paths to generated audio files.
        """
        segments = self.parse_script(script)
        results = []

        # Use provided output_dir or create temp directory
        if output_dir is None:
            output_dir = Path(tempfile.mkdtemp(prefix=f"podcast_{episode_id}_"))

        output_dir.mkdir(parents=True, exist_ok=True)

        print(f"Generating {len(segments)} audio segments...")

        for i, seg in enumerate(segments):
            print(f"  [{i+1}/{len(segments)}] Generating {seg['speaker']}: {seg['text'][:50]}...")

            try:
                # Generate audio
                audio_bytes = await self.generate_segment(seg["speaker"], seg["text"])

                # Save to local file
                segment_path = output_dir / f"segment_{i:03d}_{seg['speaker']}.mp3"
                segment_path.write_bytes(audio_bytes)

                # Estimate duration (rough: 150 wpm)
                duration_ms = self.estimate_duration(seg["text"])

                results.append(AudioSegment(
                    speaker=seg["speaker"],
                    text=seg["text"],
                    voice_id=seg["voice_id"],
                    audio_path=str(segment_path),
                    duration_ms=duration_ms
                ))

            except Exception as e:
                print(f"  ERROR generating segment {i}: {e}")
                raise

        print(f"Generated {len(results)} segments to {output_dir}")
        return results

    def estimate_duration(self, text: str) -> int:
        """Estimate speech duration in milliseconds (rough: 150 wpm)."""
        words = len(text.split())
        minutes = words / 150
        return int(minutes * 60 * 1000)

    async def generate_single_voice(
        self,
        text: str,
        speaker: str = "doug",
        output_path: Path | None = None
    ) -> Path:
        """Generate a single audio file for testing."""
        audio_bytes = await self.generate_segment(speaker, text)

        if output_path is None:
            output_path = Path(tempfile.mktemp(suffix=".mp3"))

        output_path.write_bytes(audio_bytes)
        return output_path
