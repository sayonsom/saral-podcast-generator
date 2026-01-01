"""Blog routes."""
from fastapi import APIRouter, UploadFile, HTTPException
import frontmatter

from app.models import Blog

router = APIRouter()

# In-memory store for scaffold (replace with Firestore)
_blogs: dict[str, Blog] = {}


@router.post("/upload")
async def upload_blog(file: UploadFile) -> Blog:
    """Upload markdown blog file."""
    content = await file.read()
    text = content.decode("utf-8")
    
    # Parse frontmatter if present
    post = frontmatter.loads(text)
    
    blog = Blog(
        title=post.get("title", file.filename or "Untitled"),
        content=post.content,
        summary=post.get("summary"),
        tags=post.get("tags", [])
    )
    
    _blogs[blog.id] = blog
    return blog


@router.post("/")
async def create_blog(title: str, content: str) -> Blog:
    """Create blog from raw content."""
    blog = Blog(title=title, content=content)
    _blogs[blog.id] = blog
    return blog


@router.get("/")
async def list_blogs() -> list[Blog]:
    """List all blogs."""
    return list(_blogs.values())


@router.get("/{blog_id}")
async def get_blog(blog_id: str) -> Blog:
    """Get blog by ID."""
    if blog_id not in _blogs:
        raise HTTPException(status_code=404, detail="Blog not found")
    return _blogs[blog_id]


@router.delete("/{blog_id}")
async def delete_blog(blog_id: str) -> dict:
    """Delete blog."""
    if blog_id not in _blogs:
        raise HTTPException(status_code=404, detail="Blog not found")
    del _blogs[blog_id]
    return {"deleted": blog_id}
