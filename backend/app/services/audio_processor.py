"""Audio processing: join segments, add music, normalize."""
import tempfile
from pathlib import Path

from pydub import AudioSegment
from pydub.effects import normalize, compress_dynamic_range

from app.config import settings


class AudioProcessor:
    """
    Join audio segments with intro/outro music.
    Normalize levels for podcast standards.
    """

    def __init__(self):
        # Local paths for intro/outro (can be overridden)
        self.intro_path: Path | None = None
        self.outro_path: Path | None = None

        # Timing settings (ms)
        self.crossfade_intro = 1500      # Crossfade from intro to speech
        self.crossfade_outro = 2000      # Crossfade from speech to outro
        self.pause_between_speakers = 400 # Pause between Doug/Claire

        # Output settings
        self.output_bitrate = "192k"
        self.target_lufs = -16  # Podcast standard loudness

    def set_intro_outro(self, intro_path: Path | None, outro_path: Path | None):
        """Set paths for intro/outro music files."""
        self.intro_path = intro_path
        self.outro_path = outro_path

    def join_segments(
        self,
        segment_paths: list[str | Path],
        output_path: Path | None = None
    ) -> Path:
        """
        Join speech segments with pauses between speakers.

        Args:
            segment_paths: List of paths to MP3 segment files
            output_path: Where to save the joined audio

        Returns:
            Path to the joined audio file
        """
        if not segment_paths:
            raise ValueError("No segments provided")

        speech = AudioSegment.empty()

        for i, path in enumerate(segment_paths):
            segment = AudioSegment.from_mp3(str(path))

            # Add pause between speakers (not before first)
            if len(speech) > 0:
                speech += AudioSegment.silent(duration=self.pause_between_speakers)

            speech += segment

        # Normalize
        speech = normalize(speech)

        # Output path
        if output_path is None:
            output_path = Path(tempfile.mktemp(suffix=".mp3"))

        speech.export(
            str(output_path),
            format="mp3",
            bitrate=self.output_bitrate
        )

        return output_path

    def finalize_episode(
        self,
        segment_paths: list[str | Path],
        output_path: Path | None = None
    ) -> dict:
        """
        Full audio pipeline:
        1. Join segments with pauses
        2. Add intro/outro with crossfades (if available)
        3. Normalize audio levels
        4. Apply light compression
        5. Export final MP3

        Returns:
            Dict with output_path, duration_seconds, file_size_mb
        """
        if not segment_paths:
            raise ValueError("No segments provided")

        # Join speech segments
        speech = AudioSegment.empty()

        for i, path in enumerate(segment_paths):
            segment = AudioSegment.from_mp3(str(path))

            if len(speech) > 0:
                speech += AudioSegment.silent(duration=self.pause_between_speakers)

            speech += segment

        # Build final audio
        final = speech

        # Add intro if available
        if self.intro_path and self.intro_path.exists():
            intro = AudioSegment.from_mp3(str(self.intro_path))
            final = intro.append(speech, crossfade=self.crossfade_intro)

        # Add outro if available
        if self.outro_path and self.outro_path.exists():
            outro = AudioSegment.from_mp3(str(self.outro_path))
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

        # Output path
        if output_path is None:
            output_path = Path(tempfile.mktemp(suffix=".mp3"))

        # Export
        final.export(
            str(output_path),
            format="mp3",
            bitrate=self.output_bitrate,
            tags={
                "artist": "Energy Debates",
                "album": "Energy Debates Podcast"
            }
        )

        return {
            "output_path": str(output_path),
            "duration_seconds": len(final) // 1000,
            "file_size_mb": round(output_path.stat().st_size / (1024 * 1024), 2)
        }

    def get_duration_estimate(self, segment_count: int, avg_segment_ms: int = 15000) -> int:
        """Estimate total duration in seconds."""
        speech_ms = segment_count * avg_segment_ms
        intro_outro_ms = 25000  # ~25 seconds total
        pauses_ms = (segment_count - 1) * self.pause_between_speakers
        total_ms = speech_ms + intro_outro_ms + pauses_ms
        return total_ms // 1000


# Convenience function for quick processing
async def process_episode_audio(
    segment_paths: list[str | Path],
    output_path: Path,
    intro_path: Path | None = None,
    outro_path: Path | None = None
) -> dict:
    """
    Process episode audio with optional intro/outro.

    This is a convenience wrapper for AudioProcessor.
    """
    processor = AudioProcessor()
    processor.set_intro_outro(intro_path, outro_path)
    return processor.finalize_episode(segment_paths, output_path)
