"""Episode routes."""
from typing import Literal
from fastapi import APIRouter, HTTPException
from fastapi.responses import PlainTextResponse

from app.models import Episode, GenerationSettings
from app.routes.blogs import _blogs
from app.services.script_generator import ScriptGenerator

router = APIRouter()

# In-memory store (replace with Firestore)
_episodes: dict[str, Episode] = {}


def _get_previous_summary() -> str:
    """Get most recent episode summary for callbacks."""
    if not _episodes:
        return "This is the first episode of Energy Debates!"
    
    latest = max(_episodes.values(), key=lambda e: e.created_at)
    return latest.summary or "Last episode covered energy policy developments."


@router.post("/generate")
async def generate_episode(
    blog_id: str,
    settings: GenerationSettings | None = None
) -> Episode:
    """Generate podcast script from blog."""
    if blog_id not in _blogs:
        raise HTTPException(status_code=404, detail="Blog not found")
    
    blog = _blogs[blog_id]
    gen_settings = settings or GenerationSettings()
    
    generator = ScriptGenerator()
    episode = await generator.generate(
        blog=blog,
        gen_settings=gen_settings,
        previous_summary=_get_previous_summary()
    )
    
    _episodes[episode.id] = episode
    return episode


@router.get("/")
async def list_episodes() -> list[Episode]:
    """List all episodes."""
    return sorted(_episodes.values(), key=lambda e: e.created_at, reverse=True)


@router.get("/{episode_id}")
async def get_episode(episode_id: str) -> Episode:
    """Get episode by ID."""
    if episode_id not in _episodes:
        raise HTTPException(status_code=404, detail="Episode not found")
    return _episodes[episode_id]


@router.get("/{episode_id}/export")
async def export_episode(
    episode_id: str,
    format: Literal["txt", "teleprompter"] = "txt"
) -> PlainTextResponse:
    """Export script as plain text."""
    if episode_id not in _episodes:
        raise HTTPException(status_code=404, detail="Episode not found")
    
    episode = _episodes[episode_id]
    
    if format == "teleprompter":
        # Large text, speaker labels prominent
        lines = episode.script.split("\n")
        formatted = []
        for line in lines:
            if line.startswith("DOUG:") or line.startswith("CLAIRE:"):
                formatted.append(f"\n{'='*40}\n{line}")
            else:
                formatted.append(line)
        content = "\n".join(formatted)
    else:
        content = episode.script
    
    return PlainTextResponse(
        content=content,
        media_type="text/plain",
        headers={"Content-Disposition": f'attachment; filename="{episode.title}.txt"'}
    )


@router.delete("/{episode_id}")
async def delete_episode(episode_id: str) -> dict:
    """Delete episode."""
    if episode_id not in _episodes:
        raise HTTPException(status_code=404, detail="Episode not found")
    del _episodes[episode_id]
    return {"deleted": episode_id}
