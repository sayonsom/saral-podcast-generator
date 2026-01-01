"""Publishing routes: metadata, thumbnail, Spotify upload."""
import json
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from anthropic import AsyncAnthropic

from app.config import settings

router = APIRouter()

# In-memory storage (replace with Firestore)
_metadata: dict[str, dict] = {}
_thumbnails: dict[str, str] = {}


class Chapter(BaseModel):
    title: str
    start_time: str  # HH:MM:SS


class PublishMetadata(BaseModel):
    episode_id: str
    title: str
    description: str
    keywords: list[str]
    chapters: list[Chapter]
    search_terms: list[str]
    thumbnail_url: str | None = None


METADATA_PROMPT = """Generate podcast episode metadata for Spotify distribution.

EPISODE TITLE: {title}
EPISODE SUMMARY: {summary}
KEY INSIGHTS:
{insights}

Generate the following:

1. DESCRIPTION (2-3 paragraphs):
   - Opening hook that grabs attention
   - What Doug and Claire debate in this episode
   - Key takeaways for different audiences (utilities, startups, consumers)
   - Call to action: subscribe and leave a review
   - Include: "Based on Dr. Cheyenne's analysis at askespresso.com"

2. KEYWORDS (8-12 tags for discoverability):
   - Mix of broad terms (energy, utilities, podcast)
   - Specific terms related to episode topic
   - Always include: "energy debates podcast", "energy policy"

3. CHAPTERS (from the script timing):
   - Format each as: {{"title": "Chapter Name", "start_time": "MM:SS"}}
   - Include: Intro, main discussion segments, Outro

4. SEARCH_TERMS (3-5 terms for Unsplash thumbnail search):
   - Relevant imagery: power grid, solar, wind, energy, electricity
   - Avoid: generic business, office, people stock photos
   - Prefer: dramatic infrastructure, energy landscapes

Output as JSON with keys: description, keywords, chapters, search_terms"""


@router.post("/metadata/{episode_id}")
async def generate_metadata(episode_id: str) -> PublishMetadata:
    """Generate Spotify-ready metadata from episode."""
    from app.routes.episodes import _episodes
    
    if episode_id not in _episodes:
        raise HTTPException(status_code=404, detail="Episode not found")
    
    episode = _episodes[episode_id]
    
    # Generate metadata with Claude
    client = AsyncAnthropic(api_key=settings.anthropic_api_key)
    
    prompt = METADATA_PROMPT.format(
        title=episode.title,
        summary=episode.summary,
        insights=json.dumps(episode.insights.model_dump(), indent=2)
    )
    
    response = await client.messages.create(
        model=settings.anthropic_model,
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}]
    )
    
    # Parse response
    data = json.loads(response.content[0].text)
    
    metadata = PublishMetadata(
        episode_id=episode_id,
        title=episode.title,
        description=data["description"],
        keywords=data["keywords"],
        chapters=[Chapter(**ch) for ch in data["chapters"]],
        search_terms=data["search_terms"]
    )
    
    _metadata[episode_id] = metadata.model_dump()
    
    return metadata


@router.get("/metadata/{episode_id}")
async def get_metadata(episode_id: str) -> PublishMetadata:
    """Get previously generated metadata."""
    if episode_id not in _metadata:
        raise HTTPException(status_code=404, detail="Metadata not found. Generate first.")
    
    return PublishMetadata(**_metadata[episode_id])


@router.post("/thumbnail/{episode_id}")
async def generate_thumbnail(episode_id: str) -> dict:
    """Generate episode thumbnail using Unsplash + branding."""
    from app.routes.episodes import _episodes
    from app.services.thumbnail_generator import ThumbnailGenerator
    from app.services.storage import storage
    
    if episode_id not in _episodes:
        raise HTTPException(status_code=404, detail="Episode not found")
    
    episode = _episodes[episode_id]
    
    # Get metadata for search terms (or use defaults)
    if episode_id in _metadata:
        search_terms = _metadata[episode_id].get("search_terms", [])
    else:
        search_terms = ["power grid", "energy", "electricity"]
    
    # Get episode number
    episode_count = len(_episodes)
    
    # Generate thumbnail
    generator = ThumbnailGenerator()
    image_bytes = await generator.generate(
        search_terms=search_terms,
        episode_title=episode.title.replace("Energy Debates: ", ""),
        episode_number=episode_count
    )
    
    # Upload to storage
    path = f"thumbnails/{episode_id}_thumb.jpg"
    url = await storage.upload_image(image_bytes, path)
    
    _thumbnails[episode_id] = url
    
    # Update metadata if exists
    if episode_id in _metadata:
        _metadata[episode_id]["thumbnail_url"] = url
    
    return {"thumbnail_url": url}


@router.get("/thumbnail/{episode_id}")
async def get_thumbnail(episode_id: str) -> dict:
    """Get thumbnail URL for episode."""
    if episode_id not in _thumbnails:
        raise HTTPException(status_code=404, detail="Thumbnail not found. Generate first.")
    
    return {"thumbnail_url": _thumbnails[episode_id]}


# --- Spotify OAuth Flow ---

@router.get("/spotify/auth")
async def spotify_auth(request: Request):
    """Redirect to Spotify OAuth."""
    from app.services.spotify_publisher import SpotifyPublisher
    
    publisher = SpotifyPublisher()
    auth_url = publisher.get_auth_url(state="energy_debates")
    
    return RedirectResponse(auth_url)


@router.get("/spotify/callback")
async def spotify_callback(code: str, state: str = ""):
    """Handle Spotify OAuth callback."""
    from app.services.spotify_publisher import SpotifyPublisher
    
    publisher = SpotifyPublisher()
    credentials = await publisher.exchange_code(code)
    
    # Store credentials (in production, encrypt and store securely)
    # For now, return success message
    
    return {
        "status": "authenticated",
        "message": "Spotify connected successfully",
        "expires_at": credentials.expires_at.isoformat()
    }


@router.post("/spotify/{episode_id}")
async def publish_to_spotify(episode_id: str) -> dict:
    """
    Prepare episode for Spotify publication.
    
    Note: Since Spotify for Podcasters doesn't have a public upload API,
    this returns instructions and prepared files for manual upload.
    
    For automated distribution, use the RSS feed endpoint.
    """
    from app.routes.episodes import _episodes
    from app.routes.audio import _audio_jobs
    from app.services.spotify_publisher import SpotifyPublisher
    
    if episode_id not in _episodes:
        raise HTTPException(status_code=404, detail="Episode not found")
    
    if episode_id not in _metadata:
        raise HTTPException(status_code=400, detail="Generate metadata first")
    
    # Find completed audio job
    audio_job = None
    for job in _audio_jobs.values():
        if job["episode_id"] == episode_id and job["status"] == "complete":
            audio_job = job
            break
    
    if not audio_job:
        raise HTTPException(status_code=400, detail="Generate audio first")
    
    metadata = _metadata[episode_id]
    thumbnail_url = _thumbnails.get(episode_id)
    
    if not thumbnail_url:
        raise HTTPException(status_code=400, detail="Generate thumbnail first")
    
    # Prepare for upload
    publisher = SpotifyPublisher()
    
    prepared_metadata = publisher.prepare_episode_metadata(
        title=metadata["title"],
        description=metadata["description"],
        keywords=metadata["keywords"],
        chapters=metadata["chapters"],
        duration_seconds=audio_job["duration_seconds"],
        explicit=False
    )
    
    instructions = await publisher.get_upload_instructions(
        audio_path=audio_job["output_path"],
        thumbnail_path=thumbnail_url,
        metadata=prepared_metadata
    )
    
    return instructions


@router.get("/rss/{episode_id}")
async def get_rss_item(episode_id: str) -> dict:
    """
    Get RSS feed item XML for this episode.
    
    Add this to your podcast RSS feed for automatic distribution
    to Spotify, Apple Podcasts, and other platforms.
    """
    from app.routes.audio import _audio_jobs
    from app.services.spotify_publisher import SpotifyPublisher
    
    if episode_id not in _metadata:
        raise HTTPException(status_code=400, detail="Generate metadata first")
    
    # Find completed audio job
    audio_job = None
    for job in _audio_jobs.values():
        if job["episode_id"] == episode_id and job["status"] == "complete":
            audio_job = job
            break
    
    if not audio_job:
        raise HTTPException(status_code=400, detail="Generate audio first")
    
    metadata = _metadata[episode_id]
    thumbnail_url = _thumbnails.get(episode_id, "")
    
    publisher = SpotifyPublisher()
    
    prepared = publisher.prepare_episode_metadata(
        title=metadata["title"],
        description=metadata["description"],
        keywords=metadata["keywords"],
        chapters=metadata["chapters"],
        duration_seconds=audio_job["duration_seconds"]
    )
    
    rss_xml = publisher.generate_rss_item(
        metadata=prepared,
        audio_url=audio_job["output_path"],
        thumbnail_url=thumbnail_url,
        guid=episode_id
    )
    
    return {"rss_item": rss_xml}
