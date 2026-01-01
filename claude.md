# CLAUDE.md - Energy Debates Podcast Generator

## Project Context

Converting energy industry blog posts into debate-style podcast scripts between Doug (conservative FERC lawyer) and Claire (progressive McKinsey consultant).

## Tech Stack

- **Backend**: Python 3.11+, FastAPI, Pydantic v2, Docker
- **Frontend**: Next.js 14 (App Router), TypeScript, Tailwind CSS
- **Design**: Microsoft Fluent-inspired, CircularStd font, primary color `#ea580b`
- **AI**: Anthropic Claude API (claude-sonnet-4-20250514)
- **Deployment**: GCP (Cloud Run, Firestore, Cloud Storage)

## Directory Structure

```
podcast-generator/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── models/
│   │   │   ├── blog.py
│   │   │   ├── episode.py
│   │   │   └── character.py
│   │   ├── routes/
│   │   │   ├── blogs.py
│   │   │   ├── episodes.py
│   │   │   └── settings.py
│   │   ├── services/
│   │   │   ├── blog_parser.py
│   │   │   ├── script_generator.py
│   │   │   ├── research_expander.py
│   │   │   └── storage.py
│   │   ├── prompts/
│   │   │   ├── __init__.py
│   │   │   ├── analysis.py
│   │   │   ├── research.py
│   │   │   ├── outline.py
│   │   │   └── script.py
│   │   └── db/
│   │       └── firestore.py
│   ├── Dockerfile
│   ├── requirements.txt
│   └── tests/
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   ├── components/
│   │   └── lib/
│   ├── tailwind.config.ts
│   └── package.json
└── docker-compose.yml
```

## Key Prompts

### PROMPT 1: Blog Analysis

```python
BLOG_ANALYSIS_PROMPT = """
You are an energy industry analyst preparing a podcast brief.

Analyze this blog post and extract:
1. KEY_FACTS: Specific data points, statistics, dates, figures
2. MAIN_ARGUMENTS: Core thesis and supporting claims  
3. STAKEHOLDERS: Who is affected (utilities, consumers, regulators, startups)
4. CONTROVERSY_POINTS: Elements that could spark debate
5. REGULATORY_HOOKS: Any FERC, PUC, or policy implications

Blog Content:
{blog_content}

Output as JSON with these exact keys.
"""
```

### PROMPT 2: Research Expansion

```python
RESEARCH_EXPANSION_PROMPT = """
You are a senior energy economist at a top consulting firm.

Given these facts from a blog post:
{key_facts}

Generate deeper insights that weren't explicitly stated:

SECOND_DEGREE_INSIGHTS (direct implications):
- What does this mean for utility planning cycles?
- How might this affect retail rate cases?
- What startup opportunities emerge?

THIRD_DEGREE_INSIGHTS (downstream effects):
- Long-term grid architecture implications
- Consumer behavior changes
- Market structure evolution
- Regulatory precedent risks

EXPERT_QUESTIONS:
- What would a FERC commissioner ask about this?
- What would a utility CFO want to know?
- What would a cleantech VC focus on?

Be specific. Reference real market dynamics. Think like someone with 20+ years in the industry.
"""
```

### PROMPT 3: Script Outline

```python
SCRIPT_OUTLINE_PROMPT = """
Create a podcast script outline for "Energy Debates" episode.

CHARACTERS:
- DOUG (Host): Retired FERC lawyer, conservative, dry wit, loves regulatory history,
  skeptical of rapid change, respects market mechanisms. Catchphrases: "Well now...",
  "Back in my FERC days...", "The docket says otherwise"
  
- CLAIRE (Commentator): Ex-McKinsey, now at Espresso Consulting, progressive but pragmatic,
  data-driven, pro-innovation. Catchphrases: "The numbers tell a different story...",
  "Our clients are seeing...", "Let me push back on that"

TOPIC: {topic}
KEY FACTS: {key_facts}
INSIGHTS: {insights}

PREVIOUS EPISODE SUMMARY (for callbacks): {previous_summary}

Create outline with:
1. COLD_OPEN: Banter (weather, industry gossip, light personal)
2. INTRO: Doug sets up topic with slight skepticism
3. SEGMENTS: 3-4 debate segments, each with:
   - Doug's position
   - Claire's counter
   - Point of agreement
4. STAKEHOLDER_ROUNDUP: Quick takes for utilities/consumers/startups
5. CLOSE: Teaser for next topic, friendly sign-off

Include [HUMOR_BEAT] markers where jokes should go.
Must reference: "as Dr. Cheyenne wrote on his blog at askespresso.com"
"""
```

### PROMPT 4: Full Script Generation

```python
FULL_SCRIPT_PROMPT = """
Write the complete podcast script based on this outline:
{outline}

STYLE GUIDE:
- Natural speech patterns (ums, wells, you knows - sparingly)
- Stage directions in brackets: [laughs], [sighs], [paper shuffling]
- Timing markers: [00:00], [05:00], etc.
- Both hosts are LIKEABLE despite disagreements
- Humor comes from mutual respect and self-awareness
- Doug occasionally admits Claire has a point (and vice versa)
- Inside jokes that reward loyal listeners
- NO strawmanning - both positions have merit

DOUG'S VOICE:
- Formal but warm, like a favorite professor
- Historical references to FERC cases
- Skeptical questions, not attacks
- Admits when markets surprise him

CLAIRE'S VOICE:
- Consultant-speak but self-aware about it
- Leads with data, not ideology
- Acknowledges implementation challenges
- Respects Doug's regulatory knowledge

LENGTH: Approximately {duration} minutes of dialogue
HUMOR_LEVEL: {humor_level}/5

Attribution reminder: Reference "Dr. Cheyenne's blog at askespresso.com" at least twice.

Output the script with clear speaker labels (DOUG: / CLAIRE:).
"""
```

## Character Profiles (Default)

```python
DOUG_PROFILE = {
    "name": "Doug Morrison",
    "role": "Host",
    "background": "35 years at FERC, retired Deputy General Counsel. Georgetown Law. Started when PURPA was new.",
    "political_lean": "Conservative, free-market, skeptical of subsidies",
    "speech_patterns": [
        "Long pauses before making a point",
        "References to specific docket numbers",
        "Rhetorical questions",
        "Self-deprecating humor about his age"
    ],
    "catchphrases": [
        "Well now, let me tell you...",
        "Back when Order 888 was just a gleam in someone's eye...",
        "The market has a way of sorting these things out",
        "I've seen this movie before"
    ],
    "expertise": ["FERC precedent", "Wholesale markets", "Transmission policy", "Rate cases"]
}

CLAIRE_PROFILE = {
    "name": "Claire Nakamura",  
    "role": "Commentator",
    "background": "15 years energy consulting. McKinsey partner, now Lead at Espresso Consulting. Stanford MBA, Berkeley engineering.",
    "political_lean": "Progressive, pro-innovation, pragmatic about policy",
    "speech_patterns": [
        "Leads with data and charts (describes them)",
        "Client anecdotes (anonymized)",
        "Frameworks and mental models",
        "Acknowledges complexity"
    ],
    "catchphrases": [
        "The data actually shows...",
        "I was just talking to a utility exec who said...",
        "Let me offer a different framing here",
        "Doug, you're not wrong, but..."
    ],
    "expertise": ["Utility strategy", "DER economics", "Rate design", "Customer engagement"]
}
```

## Implementation Notes

### Script Generator Service

```python
# backend/app/services/script_generator.py

class ScriptGenerator:
    """Multi-stage script generation pipeline."""
    
    async def generate(self, blog: Blog, settings: GenerationSettings) -> Episode:
        # Stage 1: Analyze blog
        analysis = await self._analyze_blog(blog.content)
        
        # Stage 2: Expand research
        insights = await self._expand_research(analysis.key_facts)
        
        # Stage 3: Get previous episode for callbacks
        prev_summary = await self._get_previous_summary()
        
        # Stage 4: Create outline
        outline = await self._create_outline(
            topic=blog.title,
            key_facts=analysis.key_facts,
            insights=insights,
            previous_summary=prev_summary
        )
        
        # Stage 5: Generate full script
        script = await self._generate_script(
            outline=outline,
            duration=settings.duration,
            humor_level=settings.humor_level
        )
        
        return Episode(
            blog_id=blog.id,
            title=f"Energy Debates: {blog.title}",
            script=script,
            insights=insights,
            summary=self._create_summary(script)  # For future callbacks
        )
```

### API Endpoints

```python
# backend/app/routes/episodes.py

@router.post("/generate")
async def generate_episode(
    blog_id: str,
    settings: GenerationSettings = GenerationSettings()
) -> Episode:
    """Generate podcast script from blog."""
    blog = await get_blog(blog_id)
    generator = ScriptGenerator()
    return await generator.generate(blog, settings)

@router.get("/{episode_id}/export")
async def export_episode(
    episode_id: str,
    format: Literal["txt", "docx", "teleprompter"] = "txt"
) -> FileResponse:
    """Export script in various formats."""
    episode = await get_episode(episode_id)
    return await export_script(episode, format)
```

## Frontend Components

Key components to build:
- `BlogUploader` - Drag-drop markdown upload
- `ScriptPreview` - Two-column speaker view
- `GenerationWizard` - Step-by-step settings
- `EpisodeCard` - Episode list item
- `CharacterEditor` - Customize Doug/Claire

## Environment Variables

```bash
# .env
ANTHROPIC_API_KEY=sk-ant-...
GCP_PROJECT_ID=your-project
GCS_BUCKET=podcast-generator-assets
FIRESTORE_COLLECTION=podcast_generator
```

## Testing Commands

```bash
# Backend
cd backend && pytest tests/ -v

# Frontend  
cd frontend && npm run test

# Local dev
docker-compose up --build
```

## Common Tasks

1. **Add new catchphrase**: Update character profiles in `prompts/__init__.py`
2. **Adjust humor**: Modify `FULL_SCRIPT_PROMPT` examples
3. **New export format**: Add handler in `services/export.py`
4. **Change AI model**: Update `config.py` MODEL constant

---

## Phase 2: Audio Generation

### Audio Directory Structure

```
backend/app/
├── services/
│   ├── script_generator.py
│   ├── audio_generator.py      # ElevenLabs TTS
│   ├── audio_processor.py      # Join, normalize, crossfade
│   └── storage.py              # GCS upload/download
├── routes/
│   ├── audio.py
│   └── publish.py
```

### PROMPT: Episode Metadata Generation

```python
METADATA_PROMPT = """Generate podcast episode metadata for Spotify.

EPISODE TITLE: {title}
SCRIPT SUMMARY: {summary}
KEY TOPICS: {topics}

Generate:

1. DESCRIPTION (2-3 paragraphs):
   - Hook sentence that grabs attention
   - What Doug and Claire debate this episode
   - Key takeaways for listeners
   - Call to action (subscribe, leave review)
   - Include: "Based on Dr. Cheyenne's analysis at askespresso.com"

2. KEYWORDS (8-12 tags):
   - Mix of broad (energy, utilities) and specific (FERC Order 2222, DER)
   - Include "energy debates podcast"
   
3. CHAPTERS (timestamps from script):
   - Format: HH:MM:SS - Title
   - Include: Intro, each main segment, Outro

4. SEARCH_TERMS (for Unsplash thumbnail):
   - 3-5 relevant image search terms
   - Prefer: energy, power, grid, electricity imagery
   - Avoid: generic business stock photos

Output as JSON with keys: description, keywords, chapters, search_terms
"""
```

### Audio Generator Service

```python
# backend/app/services/audio_generator.py

from elevenlabs import ElevenLabs, VoiceSettings
import re

class AudioGenerator:
    """Generate speech from script using ElevenLabs."""
    
    def __init__(self):
        self.client = ElevenLabs(api_key=settings.elevenlabs_api_key)
        self.voices = {
            "doug": settings.elevenlabs_doug_voice_id,
            "claire": settings.elevenlabs_claire_voice_id,
        }
        self.voice_settings = VoiceSettings(
            stability=0.5,
            similarity_boost=0.75,
            style=0.0,
            use_speaker_boost=True
        )
    
    def parse_script(self, script: str) -> list[dict]:
        """Parse script into speaker segments."""
        segments = []
        pattern = r'(DOUG|CLAIRE):\s*(.+?)(?=(?:DOUG|CLAIRE):|$)'
        
        for match in re.finditer(pattern, script, re.DOTALL):
            speaker = match.group(1).lower()
            text = match.group(2).strip()
            # Remove stage directions
            text = re.sub(r'\[.*?\]', '', text).strip()
            if text:
                segments.append({"speaker": speaker, "text": text})
        
        return segments
    
    async def generate_segment(self, speaker: str, text: str) -> bytes:
        """Generate audio for single segment."""
        voice_id = self.voices[speaker]
        
        audio = await self.client.text_to_speech.convert(
            voice_id=voice_id,
            text=text,
            model_id="eleven_multilingual_v2",
            voice_settings=self.voice_settings
        )
        
        return audio
    
    async def generate_full_episode(self, script: str) -> list[AudioSegment]:
        """Generate all segments, return paths."""
        segments = self.parse_script(script)
        results = []
        
        for i, seg in enumerate(segments):
            audio_bytes = await self.generate_segment(seg["speaker"], seg["text"])
            path = await storage.upload_audio(audio_bytes, f"segment_{i}.mp3")
            results.append(AudioSegment(
                speaker=seg["speaker"],
                text=seg["text"],
                audio_path=path
            ))
        
        return results
```

### Audio Processor Service

```python
# backend/app/services/audio_processor.py

from pydub import AudioSegment
from pydub.effects import normalize, compress_dynamic_range

class AudioProcessor:
    """Join and process audio segments into final podcast."""
    
    def __init__(self):
        self.intro_path = "gs://bucket/audio/intro.mp3"
        self.outro_path = "gs://bucket/audio/outro.mp3"
        self.crossfade_ms = 1500
        self.pause_between_speakers_ms = 300
    
    async def finalize_episode(
        self,
        segment_paths: list[str],
        output_path: str
    ) -> str:
        """Join intro + segments + outro with processing."""
        
        # Load intro/outro
        intro = AudioSegment.from_mp3(await storage.download(self.intro_path))
        outro = AudioSegment.from_mp3(await storage.download(self.outro_path))
        
        # Load and join speech segments
        speech = AudioSegment.empty()
        for path in segment_paths:
            segment = AudioSegment.from_mp3(await storage.download(path))
            if len(speech) > 0:
                speech += AudioSegment.silent(duration=self.pause_between_speakers_ms)
            speech += segment
        
        # Join with crossfades
        final = intro.append(speech, crossfade=self.crossfade_ms)
        final = final.append(outro, crossfade=self.crossfade_ms)
        
        # Normalize and compress for podcast standards
        final = normalize(final)
        final = compress_dynamic_range(final)
        
        # Export
        final.export(output_path, format="mp3", bitrate="192k")
        
        return await storage.upload(output_path)
```

### Thumbnail Generator Service

```python
# backend/app/services/thumbnail_generator.py

import httpx
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

class ThumbnailGenerator:
    """Generate episode artwork using Unsplash + text overlay."""
    
    def __init__(self):
        self.unsplash_key = settings.unsplash_access_key
        self.size = (3000, 3000)  # Spotify spec
        self.brand_color = "#ea580b"
    
    async def search_image(self, query: str) -> str:
        """Search Unsplash for relevant image."""
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                "https://api.unsplash.com/search/photos",
                params={
                    "query": query,
                    "orientation": "squarish",
                    "per_page": 1
                },
                headers={"Authorization": f"Client-ID {self.unsplash_key}"}
            )
            data = resp.json()
            return data["results"][0]["urls"]["regular"]
    
    async def generate(
        self,
        search_terms: list[str],
        episode_title: str,
        episode_number: int
    ) -> bytes:
        """Generate branded thumbnail."""
        
        # Get background image
        query = " ".join(search_terms[:3])
        image_url = await self.search_image(query)
        
        async with httpx.AsyncClient() as client:
            resp = await client.get(image_url)
            bg = Image.open(BytesIO(resp.content))
        
        # Resize and crop to square
        bg = bg.resize(self.size, Image.LANCZOS)
        
        # Add dark overlay for text readability
        overlay = Image.new('RGBA', self.size, (0, 0, 0, 128))
        bg.paste(overlay, mask=overlay)
        
        # Add text
        draw = ImageDraw.Draw(bg)
        
        # Episode number badge
        # Title
        # "Energy Debates" branding
        # (font loading and positioning logic here)
        
        # Export
        output = BytesIO()
        bg.save(output, format="JPEG", quality=95)
        return output.getvalue()
```

---

## Phase 3: Spotify Publishing

### Spotify Service

```python
# backend/app/services/spotify_publisher.py

import httpx
from app.config import settings

class SpotifyPublisher:
    """Upload episodes to Spotify for Podcasters."""
    
    def __init__(self):
        self.client_id = settings.spotify_client_id
        self.client_secret = settings.spotify_client_secret
        self.show_id = settings.spotify_show_id
        self.token = None  # Set after OAuth
    
    def get_auth_url(self) -> str:
        """Get OAuth authorization URL."""
        return (
            "https://accounts.spotify.com/authorize?"
            f"client_id={self.client_id}&"
            "response_type=code&"
            f"redirect_uri={settings.spotify_redirect_uri}&"
            "scope=ugc-image-upload user-read-private"
        )
    
    async def exchange_code(self, code: str) -> dict:
        """Exchange auth code for tokens."""
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                "https://accounts.spotify.com/api/token",
                data={
                    "grant_type": "authorization_code",
                    "code": code,
                    "redirect_uri": settings.spotify_redirect_uri,
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                }
            )
            return resp.json()
    
    async def upload_episode(
        self,
        audio_url: str,
        metadata: PublishMetadata,
        thumbnail_url: str
    ) -> str:
        """Upload episode to Spotify."""
        # Note: Spotify for Podcasters API is limited
        # May need to use their web interface or RSS feed
        # This is a placeholder for when API access expands
        
        headers = {"Authorization": f"Bearer {self.token}"}
        
        # Upload flow:
        # 1. Create episode draft
        # 2. Upload audio file
        # 3. Upload thumbnail
        # 4. Set metadata
        # 5. Publish
        
        # Return episode URL
        return f"https://open.spotify.com/episode/{episode_id}"
```

### Publishing Routes

```python
# backend/app/routes/publish.py

@router.post("/metadata/{episode_id}")
async def generate_metadata(episode_id: str) -> PublishMetadata:
    """Generate Spotify metadata from episode."""
    episode = await get_episode(episode_id)
    
    # Use Claude to generate metadata
    prompt = METADATA_PROMPT.format(
        title=episode.title,
        summary=episode.summary,
        topics=episode.insights.model_dump_json()
    )
    
    response = await claude_client.generate(prompt)
    data = json.loads(response)
    
    return PublishMetadata(
        episode_id=episode_id,
        **data
    )

@router.post("/thumbnail/{episode_id}")
async def generate_thumbnail(episode_id: str) -> dict:
    """Generate episode artwork."""
    metadata = await get_metadata(episode_id)
    
    generator = ThumbnailGenerator()
    image_bytes = await generator.generate(
        search_terms=metadata.search_terms,
        episode_title=metadata.title,
        episode_number=await get_episode_count()
    )
    
    url = await storage.upload_image(image_bytes, f"{episode_id}_thumb.jpg")
    return {"thumbnail_url": url}

@router.post("/spotify/{episode_id}")
async def publish_to_spotify(episode_id: str) -> dict:
    """Upload episode to Spotify."""
    episode = await get_episode(episode_id)
    audio_job = await get_audio_job(episode_id)
    metadata = await get_metadata(episode_id)
    
    publisher = SpotifyPublisher()
    spotify_url = await publisher.upload_episode(
        audio_url=audio_job.output_path,
        metadata=metadata,
        thumbnail_url=metadata.thumbnail_url
    )
    
    return {"spotify_url": spotify_url, "status": "published"}
```

---

## Environment Variables (Full)

```bash
# .env

# AI
ANTHROPIC_API_KEY=sk-ant-...

# Audio
ELEVENLABS_API_KEY=...
ELEVENLABS_DOUG_VOICE_ID=...      # e.g., "pNInz6obpgDQGcFmaJgB"
ELEVENLABS_CLAIRE_VOICE_ID=...    # e.g., "EXAVITQu4vr4xnSDxMaL"

# Images
UNSPLASH_ACCESS_KEY=...

# Spotify
SPOTIFY_CLIENT_ID=...
SPOTIFY_CLIENT_SECRET=...
SPOTIFY_REDIRECT_URI=http://localhost:3000/api/spotify/callback
SPOTIFY_SHOW_ID=...

# GCP
GCP_PROJECT_ID=your-project
GCS_BUCKET=podcast-generator-assets
FIRESTORE_COLLECTION=podcast_generator
```

## Updated Requirements

```
# backend/requirements.txt additions
elevenlabs==1.0.0
pydub==0.25.1
Pillow==10.2.0
httpx==0.26.0
```

## Audio File Locations

```
gs://your-bucket/audio/
├── intro.mp3          # 5-15 sec, fade out
├── outro.mp3          # 10-20 sec, fade in
├── episodes/
│   ├── {episode_id}/
│   │   ├── segments/
│   │   │   ├── segment_0.mp3
│   │   │   ├── segment_1.mp3
│   │   │   └── ...
│   │   ├── speech.mp3      # joined segments
│   │   └── final.mp3       # with intro/outro
│   └── ...
└── thumbnails/
    └── {episode_id}_thumb.jpg
```
