"""Audio generation and processing routes."""
import os
import uuid
from enum import Enum
from pathlib import Path
from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from pydantic import BaseModel

from app.models import Episode

router = APIRouter()

# In-memory job tracking (replace with Redis/Firestore in production)
_audio_jobs: dict[str, dict] = {}

# Local audio output directory
AUDIO_OUTPUT_DIR = Path(__file__).parent.parent.parent.parent / "audio_output"
AUDIO_OUTPUT_DIR.mkdir(exist_ok=True)


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
    segment_count: int | None = None


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

        # Create output directory for this episode
        episode_dir = AUDIO_OUTPUT_DIR / episode_id
        episode_dir.mkdir(exist_ok=True)

        # Stage 1: Generate speech segments
        job["status"] = JobStatus.generating
        job["message"] = "Generating speech with ElevenLabs..."
        job["progress"] = 10

        generator = AudioGenerator()
        segments = await generator.generate_full_episode(
            script=episode.script,
            episode_id=episode_id,
            output_dir=episode_dir / "segments"
        )

        job["progress"] = 60
        job["message"] = f"Generated {len(segments)} audio segments"
        job["segment_count"] = len(segments)

        # Stage 2: Join segments
        job["status"] = JobStatus.processing
        job["message"] = "Joining and normalizing audio..."
        job["progress"] = 70

        processor = AudioProcessor()
        segment_paths = [s.audio_path for s in segments if s.audio_path]

        final_path = episode_dir / "final.mp3"
        result = processor.finalize_episode(segment_paths, final_path)

        # Complete
        job["status"] = JobStatus.complete
        job["progress"] = 100
        job["message"] = "Audio generation complete"
        job["output_path"] = result["output_path"]
        job["duration_seconds"] = result["duration_seconds"]

    except Exception as e:
        import traceback
        traceback.print_exc()
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
    2. Joins segments with pauses
    3. Normalizes audio levels

    Poll /status/{job_id} for progress.
    """
    from app.routes.episodes import _episodes

    if episode_id not in _episodes:
        raise HTTPException(status_code=404, detail="Episode not found")

    # Check if there's already an active job for this episode
    for existing_job in _audio_jobs.values():
        if (existing_job["episode_id"] == episode_id and
            existing_job["status"] in [JobStatus.pending, JobStatus.generating, JobStatus.processing]):
            return AudioJob(**existing_job)

    # Create job
    job_id = str(uuid.uuid4())

    job = {
        "id": job_id,
        "episode_id": episode_id,
        "status": JobStatus.pending,
        "progress": 0,
        "message": "Queued for audio generation",
        "output_path": None,
        "duration_seconds": None,
        "segment_count": None
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


@router.get("/episode/{episode_id}/status")
async def get_episode_audio_status(episode_id: str) -> AudioJob | None:
    """Get the most recent audio job for an episode."""
    # Find most recent job for this episode
    episode_jobs = [
        job for job in _audio_jobs.values()
        if job["episode_id"] == episode_id
    ]

    if not episode_jobs:
        # Check if audio file exists
        audio_path = AUDIO_OUTPUT_DIR / episode_id / "final.mp3"
        if audio_path.exists():
            return AudioJob(
                id="existing",
                episode_id=episode_id,
                status=JobStatus.complete,
                progress=100,
                message="Audio available",
                output_path=str(audio_path),
                duration_seconds=None
            )
        return None

    # Return most recent
    return AudioJob(**episode_jobs[-1])


@router.get("/{episode_id}/download")
async def download_audio(episode_id: str):
    """Download the final audio file for an episode."""
    audio_path = AUDIO_OUTPUT_DIR / episode_id / "final.mp3"

    if not audio_path.exists():
        raise HTTPException(status_code=404, detail="Audio file not found")

    return FileResponse(
        path=str(audio_path),
        media_type="audio/mpeg",
        filename=f"energy_debates_{episode_id}.mp3"
    )


@router.get("/jobs")
async def list_jobs() -> list[AudioJob]:
    """List all audio generation jobs."""
    return [AudioJob(**job) for job in _audio_jobs.values()]


@router.delete("/job/{job_id}")
async def delete_job(job_id: str) -> dict:
    """Delete an audio job from tracking."""
    if job_id not in _audio_jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    del _audio_jobs[job_id]
    return {"deleted": job_id}
