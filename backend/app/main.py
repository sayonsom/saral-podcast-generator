"""Energy Debates Podcast Generator - FastAPI Backend."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routes import blogs, episodes, settings as settings_routes, audio, publish

app = FastAPI(
    title="Energy Debates API",
    description="Convert blog posts to debate-style podcast scripts, generate audio, publish to Spotify",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Core routes
app.include_router(blogs.router, prefix="/api/blogs", tags=["blogs"])
app.include_router(episodes.router, prefix="/api/episodes", tags=["episodes"])
app.include_router(settings_routes.router, prefix="/api/settings", tags=["settings"])

# Audio & publishing routes
app.include_router(audio.router, prefix="/api/audio", tags=["audio"])
app.include_router(publish.router, prefix="/api/publish", tags=["publish"])


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "energy-debates-api"}
