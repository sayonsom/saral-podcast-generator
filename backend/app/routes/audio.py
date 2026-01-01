"""Audio generation and processing routes."""
from enum import Enum
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel

from app.models import Episode

router = APIRouter()

# In-memory job tracking (replace with Redis/Firestore in production)
_audio_jobs: dict[str, dict] = {}


class JobStatus(str, Enum):
    pending = "pending"
    generating = "generating"
    processing = "processing"
    complete = "complete"
    failed = "failed"


class AudioJob(BaseModel):
    id: str
    episode_id: str
    status: JobStatus
    progress: int = 0  # 0-100
    message: str = ""
    output_path: str | None = None
    duration_seconds: int | None = None


async def _generate_audio_task(job_id: str, episode_id: str):
    """Background task to generate and process audio."""
    from app.routes.episodes import _episodes
    from app.services.audio_generator import AudioGenerator
    from app.services.audio_processor import AudioProcessor
    
    job = _audio_jobs[job_id]
    
    try:
        # Get episode
        if episode_id not in _episodes:
            raise ValueError("Episode not found")
        
        episode = _episodes[episode_id]
        
        # Stage 1: Generate speech segments
        job["status"] = JobStatus.generating
        job["message"] = "Generating speech with ElevenLabs..."
        job["progress"] = 10
        
        generator = AudioGenerator()
        segments = await generator.generate_full_episode(episode.script, episode_id)
        
        job["progress"] = 60
        job["message"] = f"Generated {len(segments)} audio segments"
        
        # Stage 2: Join with intro/outro
        job["status"] = JobStatus.processing
        job["message"] = "Joining audio with intro/outro music..."
        job["progress"] = 70
        
        processor = AudioProcessor()
        segment_paths = [s.audio_path for s in segments if s.audio_path]
        result = await processor.finalize_episode(segment_paths, episode_id)
        
        # Complete
        job["status"] = JobStatus.complete
        job["progress"] = 100
        job["message"] = "Audio generation complete"
        job["output_path"] = result["output_path"]
        job["duration_seconds"] = result["duration_seconds"]
        
    except Exception as e:
        job["status"] = JobStatus.failed
        job["message"] = str(e)


@router.post("/generate/{episode_id}")
async def generate_audio(
    episode_id: str,
    background_tasks: BackgroundTasks
) -> AudioJob:
    """
    Start audio generation for an episode.
    
    This is a long-running task that:
    1. Generates speech via ElevenLabs
    2. Joins segments with intro/outro music
    3. Normalizes audio levels
    
    Poll /status/{job_id} for progress.
    """
    from app.routes.episodes import _episodes
    
    if episode_id not in _episodes:
        raise HTTPException(status_code=404, detail="Episode not found")
    
    # Create job
    import uuid
    job_id = str(uuid.uuid4())
    
    job = {
        "id": job_id,
        "episode_id": episode_id,
        "status": JobStatus.pending,
        "progress": 0,
        "message": "Queued for processing",
        "output_path": None,
        "duration_seconds": None
    }
    _audio_jobs[job_id] = job
    
    # Start background task
    background_tasks.add_task(_generate_audio_task, job_id, episode_id)
    
    return AudioJob(**job)


@router.get("/status/{job_id}")
async def get_audio_status(job_id: str) -> AudioJob:
    """Get status of audio generation job."""
    if job_id not in _audio_jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return AudioJob(**_audio_jobs[job_id])


@router.post("/finalize/{episode_id}")
async def finalize_audio(episode_id: str) -> dict:
    """
    Manually trigger audio finalization.
    
    Use this if segments were generated separately
    and just need to be joined with intro/outro.
    """
    from app.services.audio_processor import AudioProcessor
    from app.services.storage import storage
    
    # Get segment paths from storage
    segment_prefix = f"episodes/{episode_id}/segments/"
    segment_paths = await storage.list_files(segment_prefix)
    
    if not segment_paths:
        raise HTTPException(status_code=404, detail="No audio segments found")
    
    processor = AudioProcessor()
    result = await processor.finalize_episode(segment_paths, episode_id)
    
    return result


@router.get("/{episode_id}/download")
async def download_audio(episode_id: str):
    """Get download URL for final audio file."""
    from app.services.storage import storage
    
    path = f"episodes/{episode_id}/final.mp3"
    
    try:
        url = await storage.get_signed_url(path)
        return {"download_url": url}
    except Exception:
        raise HTTPException(status_code=404, detail="Audio file not found")
