"""Settings routes for character customization."""
from fastapi import APIRouter

from app.models import Character
from app.prompts import DOUG_PROFILE, CLAIRE_PROFILE

router = APIRouter()


@router.get("/characters")
async def get_characters() -> dict[str, Character]:
    """Get character profiles."""
    return {
        "doug": Character(**DOUG_PROFILE, expertise_areas=DOUG_PROFILE["expertise"]),
        "claire": Character(**CLAIRE_PROFILE, expertise_areas=CLAIRE_PROFILE["expertise"])
    }


@router.get("/callbacks")
async def get_callbacks() -> list[dict]:
    """Get previous episode summaries for reference."""
    from app.routes.episodes import _episodes
    
    return [
        {"episode_id": e.id, "title": e.title, "summary": e.summary}
        for e in sorted(_episodes.values(), key=lambda x: x.created_at, reverse=True)[:10]
    ]
