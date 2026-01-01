"""Unit tests for API endpoints (without external API calls)."""
import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def sample_blog_content():
    """Load the sample blog from blog-to-podcast folder."""
    blog_path = Path(__file__).parent.parent.parent / "blog-to-podcast" / "data-center-load-growth-pjm.md"
    return blog_path.read_text()


class TestHealthEndpoint:
    """Test health check endpoint."""

    def test_health_check(self, client):
        """Health endpoint should return healthy status."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "energy-debates-api"


class TestBlogEndpoints:
    """Test blog management endpoints."""

    def test_list_blogs_empty(self, client):
        """List blogs should return empty list initially."""
        response = client.get("/api/blogs/")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_create_blog(self, client, sample_blog_content):
        """Creating a blog should return blog with ID."""
        response = client.post(
            "/api/blogs/",
            params={"title": "Test Blog", "content": sample_blog_content}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Test Blog"
        assert "id" in data
        assert len(data["id"]) > 0

    def test_get_blog(self, client, sample_blog_content):
        """Should retrieve blog by ID."""
        # Create blog first
        create_response = client.post(
            "/api/blogs/",
            params={"title": "Test Blog", "content": "Test content"}
        )
        blog_id = create_response.json()["id"]

        # Retrieve it
        response = client.get(f"/api/blogs/{blog_id}")
        assert response.status_code == 200
        assert response.json()["id"] == blog_id

    def test_get_nonexistent_blog(self, client):
        """Getting nonexistent blog should return 404."""
        response = client.get("/api/blogs/nonexistent-id")
        assert response.status_code == 404

    def test_delete_blog(self, client):
        """Should delete blog by ID."""
        # Create blog first
        create_response = client.post(
            "/api/blogs/",
            params={"title": "To Delete", "content": "Test content"}
        )
        blog_id = create_response.json()["id"]

        # Delete it
        response = client.delete(f"/api/blogs/{blog_id}")
        assert response.status_code == 200
        assert response.json()["deleted"] == blog_id

        # Verify it's gone
        get_response = client.get(f"/api/blogs/{blog_id}")
        assert get_response.status_code == 404


class TestEpisodeEndpoints:
    """Test episode management endpoints."""

    def test_list_episodes_empty(self, client):
        """List episodes should return empty list initially."""
        response = client.get("/api/episodes/")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_generate_episode_blog_not_found(self, client):
        """Generate episode should fail if blog doesn't exist."""
        response = client.post(
            "/api/episodes/generate",
            params={"blog_id": "nonexistent-blog-id"}
        )
        assert response.status_code == 404


class TestSettingsEndpoints:
    """Test settings endpoints."""

    def test_get_characters(self, client):
        """Should return Doug and Claire profiles."""
        response = client.get("/api/settings/characters")
        assert response.status_code == 200
        data = response.json()
        assert "doug" in data
        assert "claire" in data
        assert data["doug"]["name"] == "Doug Morrison"
        assert data["claire"]["name"] == "Claire Nakamura"

    def test_get_callbacks(self, client):
        """Should return list of previous episode summaries."""
        response = client.get("/api/settings/callbacks")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
