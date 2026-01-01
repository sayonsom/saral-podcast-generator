"""Multi-stage podcast script generation service."""
import json
from anthropic import AsyncAnthropic

from app.config import settings
from app.models import Blog, Episode, BlogAnalysis, Insights, GenerationSettings
from app.prompts import (
    BLOG_ANALYSIS_PROMPT,
    RESEARCH_EXPANSION_PROMPT,
    SCRIPT_OUTLINE_PROMPT,
    FULL_SCRIPT_PROMPT,
    SUMMARY_PROMPT,
    DOUG_PROFILE,
    CLAIRE_PROFILE,
)


class ScriptGenerator:
    """Multi-stage script generation pipeline."""

    def __init__(self):
        self.client = AsyncAnthropic(api_key=settings.anthropic_api_key)
        self.model = settings.anthropic_model

    async def generate(
        self,
        blog: Blog,
        gen_settings: GenerationSettings,
        previous_summary: str = "This is the first episode!"
    ) -> Episode:
        """Full generation pipeline: analyze -> expand -> outline -> script."""
        
        # Stage 1: Analyze blog content
        analysis = await self._analyze_blog(blog.content)
        
        # Stage 2: Expand with deeper research insights
        insights = await self._expand_research(analysis.key_facts)
        
        # Stage 3: Create outline
        outline = await self._create_outline(
            topic=blog.title,
            key_facts=analysis.key_facts,
            insights=insights,
            previous_summary=previous_summary
        )
        
        # Stage 4: Generate full script
        duration_map = {"short": 10, "medium": 20, "long": 30}
        duration_minutes = duration_map[gen_settings.duration]
        
        script = await self._generate_script(
            outline=outline,
            duration_minutes=duration_minutes,
            humor_level=gen_settings.humor_level
        )
        
        # Stage 5: Create summary for future callbacks
        summary = await self._create_summary(script)
        
        return Episode(
            blog_id=blog.id,
            title=f"Energy Debates: {blog.title}",
            script=script,
            duration_estimate=duration_minutes,
            humor_level=gen_settings.humor_level,
            focus_areas=gen_settings.focus_areas,
            summary=summary,
            insights=insights
        )

    async def _call_claude(self, prompt: str, max_tokens: int = 4096) -> str:
        """Make Claude API call."""
        response = await self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text

    async def _analyze_blog(self, content: str) -> BlogAnalysis:
        """Stage 1: Extract key facts and themes from blog."""
        prompt = BLOG_ANALYSIS_PROMPT.format(blog_content=content)
        response = await self._call_claude(prompt, max_tokens=2048)
        
        # Parse JSON response
        data = json.loads(response)
        return BlogAnalysis(**data)

    async def _expand_research(self, key_facts: list[str]) -> Insights:
        """Stage 2: Generate deeper insights beyond blog content."""
        prompt = RESEARCH_EXPANSION_PROMPT.format(
            key_facts="\n".join(f"- {fact}" for fact in key_facts)
        )
        response = await self._call_claude(prompt, max_tokens=3000)
        
        data = json.loads(response)
        return Insights(**data)

    async def _create_outline(
        self,
        topic: str,
        key_facts: list[str],
        insights: Insights,
        previous_summary: str
    ) -> str:
        """Stage 3: Create structured script outline."""
        prompt = SCRIPT_OUTLINE_PROMPT.format(
            doug_profile=json.dumps(DOUG_PROFILE, indent=2),
            claire_profile=json.dumps(CLAIRE_PROFILE, indent=2),
            topic=topic,
            key_facts="\n".join(f"- {fact}" for fact in key_facts),
            insights=insights.model_dump_json(indent=2),
            previous_summary=previous_summary
        )
        return await self._call_claude(prompt, max_tokens=2500)

    async def _generate_script(
        self,
        outline: str,
        duration_minutes: int,
        humor_level: int
    ) -> str:
        """Stage 4: Generate full dialogue script."""
        # Rough estimate: 150 words per minute of dialogue
        word_count = duration_minutes * 150
        
        prompt = FULL_SCRIPT_PROMPT.format(
            outline=outline,
            duration_minutes=duration_minutes,
            word_count=word_count,
            humor_level=humor_level
        )
        return await self._call_claude(prompt, max_tokens=8000)

    async def _create_summary(self, script: str) -> str:
        """Stage 5: Create callback summary for future episodes."""
        prompt = SUMMARY_PROMPT.format(script=script[:4000])  # truncate if needed
        return await self._call_claude(prompt, max_tokens=500)
