"""Audio processing: join segments, add music, normalize."""
import tempfile
from pathlib import Path

from app.config import settings

# Requires: pip install pydub
# Also requires ffmpeg installed on system
# from pydub import AudioSegment
# from pydub.effects import normalize, compress_dynamic_range


class AudioProcessor:
    """
    Join audio segments with intro/outro music.
    Normalize levels for podcast standards.
    """

    def __init__(self):
        self.intro_path = f"gs://{settings.gcs_bucket}/audio/intro.mp3"
        self.outro_path = f"gs://{settings.gcs_bucket}/audio/outro.mp3"
        
        # Timing settings (ms)
        self.crossfade_intro = 1500      # Crossfade from intro to speech
        self.crossfade_outro = 2000      # Crossfade from speech to outro
        self.pause_between_speakers = 300 # Pause between Doug/Claire
        
        # Output settings
        self.output_bitrate = "192k"
        self.target_lufs = -16  # Podcast standard loudness

    async def finalize_episode(
        self,
        segment_paths: list[str],
        episode_id: str
    ) -> dict:
        """
        Full audio pipeline:
        1. Download all segments
        2. Join with pauses
        3. Add intro/outro with crossfades
        4. Normalize audio levels
        5. Export final MP3
        """
        from pydub import AudioSegment
        from pydub.effects import normalize, compress_dynamic_range
        from app.services.storage import storage
        
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            
            # Download intro/outro
            intro_file = tmpdir / "intro.mp3"
            outro_file = tmpdir / "outro.mp3"
            await storage.download_to_file(self.intro_path, intro_file)
            await storage.download_to_file(self.outro_path, outro_file)
            
            intro = AudioSegment.from_mp3(intro_file)
            outro = AudioSegment.from_mp3(outro_file)
            
            # Download and join speech segments
            speech = AudioSegment.empty()
            
            for i, path in enumerate(segment_paths):
                seg_file = tmpdir / f"seg_{i}.mp3"
                await storage.download_to_file(path, seg_file)
                segment = AudioSegment.from_mp3(seg_file)
                
                # Add pause between speakers (not before first)
                if len(speech) > 0:
                    speech += AudioSegment.silent(duration=self.pause_between_speakers)
                
                speech += segment
            
            # Join: intro -> speech -> outro with crossfades
            final = intro.append(speech, crossfade=self.crossfade_intro)
            final = final.append(outro, crossfade=self.crossfade_outro)
            
            # Normalize audio levels
            final = normalize(final)
            
            # Light compression for consistent volume
            final = compress_dynamic_range(
                final,
                threshold=-20.0,
                ratio=4.0,
                attack=5.0,
                release=50.0
            )
            
            # Export
            output_file = tmpdir / "final.mp3"
            final.export(
                output_file,
                format="mp3",
                bitrate=self.output_bitrate,
                tags={
                    "artist": "Energy Debates",
                    "album": "Energy Debates Podcast"
                }
            )
            
            # Upload to storage
            output_path = f"episodes/{episode_id}/final.mp3"
            final_url = await storage.upload_file(output_file, output_path)
            
            return {
                "output_path": final_url,
                "duration_seconds": len(final) // 1000,
                "file_size_mb": output_file.stat().st_size / (1024 * 1024)
            }

    async def join_segments_only(
        self,
        segment_paths: list[str],
        episode_id: str
    ) -> str:
        """Join speech segments without intro/outro (for preview)."""
        from pydub import AudioSegment
        from app.services.storage import storage
        
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            speech = AudioSegment.empty()
            
            for i, path in enumerate(segment_paths):
                seg_file = tmpdir / f"seg_{i}.mp3"
                await storage.download_to_file(path, seg_file)
                segment = AudioSegment.from_mp3(seg_file)
                
                if len(speech) > 0:
                    speech += AudioSegment.silent(duration=self.pause_between_speakers)
                speech += segment
            
            output_file = tmpdir / "speech.mp3"
            speech.export(output_file, format="mp3", bitrate=self.output_bitrate)
            
            output_path = f"episodes/{episode_id}/speech.mp3"
            return await storage.upload_file(output_file, output_path)

    def get_duration_estimate(self, segment_count: int, avg_segment_ms: int = 15000) -> int:
        """Estimate total duration in seconds."""
        speech_ms = segment_count * avg_segment_ms
        intro_outro_ms = 25000  # ~25 seconds total
        pauses_ms = (segment_count - 1) * self.pause_between_speakers
        total_ms = speech_ms + intro_outro_ms + pauses_ms
        return total_ms // 1000
