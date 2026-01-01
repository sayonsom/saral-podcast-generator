"""Test audio generation with ElevenLabs."""
import asyncio
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.audio_generator import AudioGenerator
from app.services.audio_processor import AudioProcessor


async def test_single_voice():
    """Test generating a single voice clip."""
    print("Testing single voice generation...")

    generator = AudioGenerator()

    # Test Doug's voice
    doug_text = "Well now, let me tell you about the energy markets. Back in my FERC days, we saw this coming."
    output_path = Path(__file__).parent.parent.parent / "test_doug.mp3"

    print(f"Generating Doug voice to {output_path}...")
    result = await generator.generate_single_voice(doug_text, "doug", output_path)
    print(f"Generated: {result} ({result.stat().st_size / 1024:.1f} KB)")

    # Test Claire's voice
    claire_text = "The data actually shows something quite different. Our clients are seeing significant changes in the market."
    output_path = Path(__file__).parent.parent.parent / "test_claire.mp3"

    print(f"Generating Claire voice to {output_path}...")
    result = await generator.generate_single_voice(claire_text, "claire", output_path)
    print(f"Generated: {result} ({result.stat().st_size / 1024:.1f} KB)")

    print("Single voice test complete!")


async def test_script_parsing():
    """Test script parsing."""
    print("\nTesting script parsing...")

    sample_script = """
    [00:00]
    **DOUG:** Well now, let me tell you about data centers. [laughs] They're changing everything.

    **CLAIRE:** The data actually shows something quite different. [sighs] Our clients are seeing 30 gigawatts of new requests.

    **DOUG:** Back in my FERC days, we never saw anything like this. The market has a way of sorting things out.

    **CLAIRE:** Let me push back on that. The numbers tell us this is unprecedented.
    """

    generator = AudioGenerator()
    segments = generator.parse_script(sample_script)

    print(f"Parsed {len(segments)} segments:")
    for i, seg in enumerate(segments):
        print(f"  {i+1}. [{seg['speaker'].upper()}] {seg['text'][:60]}...")

    return segments


async def test_multi_segment_generation():
    """Test generating multiple segments."""
    print("\nTesting multi-segment generation...")

    sample_script = """
    **DOUG:** Well now, let me tell you about data centers. They're completely rewriting grid planning assumptions.

    **CLAIRE:** The data actually shows we're looking at over 30 gigawatts of new requests in PJM alone.

    **DOUG:** The market has a way of sorting these things out. But I've seen this movie before.
    """

    generator = AudioGenerator()
    output_dir = Path(__file__).parent.parent.parent / "test_segments"

    print(f"Generating segments to {output_dir}...")
    segments = await generator.generate_full_episode(
        script=sample_script,
        episode_id="test_episode",
        output_dir=output_dir
    )

    print(f"Generated {len(segments)} segments:")
    for seg in segments:
        path = Path(seg.audio_path) if seg.audio_path else None
        size = path.stat().st_size / 1024 if path and path.exists() else 0
        print(f"  [{seg.speaker.upper()}] {size:.1f} KB - {seg.text[:50]}...")

    return segments


async def test_audio_processing():
    """Test joining segments."""
    print("\nTesting audio processing...")

    # First generate some segments
    segments = await test_multi_segment_generation()

    if not segments:
        print("No segments to process")
        return

    # Join them
    processor = AudioProcessor()
    segment_paths = [s.audio_path for s in segments if s.audio_path]

    output_path = Path(__file__).parent.parent.parent / "test_final.mp3"

    print(f"Joining {len(segment_paths)} segments to {output_path}...")
    result = processor.finalize_episode(segment_paths, output_path)

    print(f"Final audio:")
    print(f"  Path: {result['output_path']}")
    print(f"  Duration: {result['duration_seconds']} seconds")
    print(f"  Size: {result['file_size_mb']} MB")


async def main():
    """Run all tests."""
    print("=" * 60)
    print("ElevenLabs Audio Generation Tests")
    print("=" * 60)

    # Test 1: Single voice
    await test_single_voice()

    # Test 2: Script parsing
    await test_script_parsing()

    # Test 3: Multi-segment generation
    await test_multi_segment_generation()

    # Test 4: Audio processing
    await test_audio_processing()

    print("\n" + "=" * 60)
    print("All tests complete!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
