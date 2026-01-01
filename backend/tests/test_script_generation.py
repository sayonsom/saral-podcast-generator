"""Integration tests for podcast script generation."""
import asyncio
from pathlib import Path
import pytest
import sys

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.models import Blog, GenerationSettings
from app.services.script_generator import ScriptGenerator


@pytest.fixture
def sample_blog_content():
    """Load the sample blog from blog-to-podcast folder."""
    blog_path = Path(__file__).parent.parent.parent / "blog-to-podcast" / "data-center-load-growth-pjm.md"
    return blog_path.read_text()


@pytest.fixture
def sample_blog(sample_blog_content):
    """Create a Blog model from sample content."""
    return Blog(
        title="Data Centers Are Rewriting Grid Planning Assumptions in PJM",
        content=sample_blog_content,
        tags=["Load Growth", "Data Centers", "PJM"]
    )


@pytest.fixture
def short_settings():
    """Settings for a short ~5-6 minute episode."""
    return GenerationSettings(
        duration="short",  # 10 minutes target, will give ~5-6 min of core content
        humor_level=3,
        focus_areas=["utilities", "regulatory"]
    )


class TestScriptGenerator:
    """Test the multi-stage script generation pipeline."""

    @pytest.mark.asyncio
    async def test_blog_analysis(self, sample_blog):
        """Test Stage 1: Blog analysis extracts key facts."""
        generator = ScriptGenerator()
        analysis = await generator._analyze_blog(sample_blog.content)

        assert len(analysis.key_facts) > 0, "Should extract key facts"
        assert len(analysis.main_arguments) > 0, "Should identify main arguments"
        assert len(analysis.stakeholders) > 0, "Should identify stakeholders"

        # Check for expected data points from the blog
        facts_text = " ".join(analysis.key_facts).lower()
        assert "30 gw" in facts_text or "pjm" in facts_text, \
            "Should extract key statistics about data center load"

    @pytest.mark.asyncio
    async def test_research_expansion(self, sample_blog):
        """Test Stage 2: Research expansion generates deeper insights."""
        generator = ScriptGenerator()

        # First analyze to get key facts
        analysis = await generator._analyze_blog(sample_blog.content)

        # Then expand research
        insights = await generator._expand_research(analysis.key_facts)

        assert len(insights.utilities) > 0, "Should have utility insights"
        assert len(insights.regulatory) > 0, "Should have regulatory insights"
        assert len(insights.expert_questions) > 0, "Should have expert questions"

    @pytest.mark.asyncio
    async def test_full_script_generation(self, sample_blog, short_settings):
        """Test full pipeline generates a complete episode script."""
        generator = ScriptGenerator()

        episode = await generator.generate(
            blog=sample_blog,
            gen_settings=short_settings,
            previous_summary="This is the first episode!"
        )

        # Check episode metadata
        assert episode.blog_id == sample_blog.id
        assert "Energy Debates" in episode.title
        assert episode.duration_estimate == 10  # short = 10 min

        # Check script content
        assert "DOUG:" in episode.script, "Script should have Doug's dialogue"
        assert "CLAIRE:" in episode.script, "Script should have Claire's dialogue"
        assert len(episode.script) > 1000, "Script should be substantial"

        # Check for attribution
        assert "askespresso.com" in episode.script.lower() or \
               "dr. cheyenne" in episode.script.lower(), \
            "Script should include blog attribution"

        # Check summary was generated
        assert len(episode.summary) > 50, "Should generate callback summary"

        print("\n" + "="*60)
        print("GENERATED EPISODE")
        print("="*60)
        print(f"Title: {episode.title}")
        print(f"Duration: {episode.duration_estimate} minutes")
        print(f"Humor level: {episode.humor_level}")
        print("-"*60)
        print("SCRIPT PREVIEW (first 2000 chars):")
        print("-"*60)
        print(episode.script[:2000])
        print("...")
        print("-"*60)
        print(f"Total script length: {len(episode.script)} characters")
        print(f"Summary: {episode.summary}")
        print("="*60)


async def main():
    """Run a quick test of the script generator."""
    print("Loading sample blog...")
    blog_path = Path(__file__).parent.parent.parent / "blog-to-podcast" / "data-center-load-growth-pjm.md"
    content = blog_path.read_text()

    blog = Blog(
        title="Data Centers Are Rewriting Grid Planning Assumptions in PJM",
        content=content,
        tags=["Load Growth", "Data Centers", "PJM"]
    )

    settings = GenerationSettings(
        duration="short",
        humor_level=3,
        focus_areas=["utilities", "regulatory"]
    )

    print("Generating podcast script...")
    generator = ScriptGenerator()

    try:
        episode = await generator.generate(
            blog=blog,
            gen_settings=settings,
            previous_summary="This is the first episode of Energy Debates!"
        )

        print("\n" + "="*60)
        print("SUCCESS! Generated Episode")
        print("="*60)
        print(f"Title: {episode.title}")
        print(f"Duration: {episode.duration_estimate} minutes")
        print("-"*60)
        print("FULL SCRIPT:")
        print("-"*60)
        print(episode.script)
        print("-"*60)
        print(f"Summary for callbacks: {episode.summary}")
        print("="*60)

        # Save the generated script to a file for review
        output_path = Path(__file__).parent.parent.parent / "generated_script.txt"
        output_path.write_text(episode.script)
        print(f"\nScript saved to: {output_path}")

    except Exception as e:
        print(f"Error generating script: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
