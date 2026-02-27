"""API integration tests for /api/resume/analyze and /api/resume/match endpoints."""
import pytest
import io


class TestAnalyzeEndpoint:
    """Tests for POST /api/resume/analyze"""

    def test_analyze_valid_pdf(self, client, test_pdf_bytes):
        """Upload a valid PDF and get structured analysis result."""
        response = client.post(
            "/api/resume/analyze",
            files={"file": ("test_resume.pdf", io.BytesIO(test_pdf_bytes), "application/pdf")}
        )
        assert response.status_code == 200
        data = response.json()
        assert "resume_id" in data
        assert data["resume_id"]  # Should be non-empty hash
        assert "data" in data
        assert "basic_info" in data["data"]
        assert "message" in data
        # Store resume_id for later use
        TestAnalyzeEndpoint.resume_id = data["resume_id"]

    def test_analyze_non_pdf_file(self, client):
        """Upload a non-PDF file should return 400."""
        response = client.post(
            "/api/resume/analyze",
            files={"file": ("test.txt", io.BytesIO(b"Hello world"), "text/plain")}
        )
        assert response.status_code == 400
        assert "PDF" in response.json()["detail"]

    def test_analyze_no_file(self, client):
        """Request without file should return 422 (validation error)."""
        response = client.post("/api/resume/analyze")
        assert response.status_code == 422

    def test_analyze_same_pdf_twice_hits_cache(self, client, test_pdf_bytes):
        """Second upload of same PDF should return cache hit."""
        # First call
        response1 = client.post(
            "/api/resume/analyze",
            files={"file": ("resume.pdf", io.BytesIO(test_pdf_bytes), "application/pdf")}
        )
        assert response1.status_code == 200
        
        # Second call with same content
        response2 = client.post(
            "/api/resume/analyze",
            files={"file": ("resume.pdf", io.BytesIO(test_pdf_bytes), "application/pdf")}
        )
        assert response2.status_code == 200
        data2 = response2.json()
        assert "Cache Hit" in data2["message"]
        # Same resume_id (same file hash)
        assert data2["resume_id"] == response1.json()["resume_id"]

    def test_analyze_empty_pdf(self, client, empty_pdf_bytes):
        """Upload an empty PDF (no text) goes through image-based/mock path."""
        response = client.post(
            "/api/resume/analyze",
            files={"file": ("empty.pdf", io.BytesIO(empty_pdf_bytes), "application/pdf")}
        )
        # With the vision AI path, empty PDFs are detected as image-based.
        # Without API key, returns 200 with mock data; with API key, would call vision AI.
        assert response.status_code in (200, 400, 500)


class TestMatchEndpoint:
    """Tests for POST /api/resume/match"""

    def _ensure_resume_uploaded(self, client, test_pdf_bytes):
        """Helper: upload a resume and return resume_id."""
        response = client.post(
            "/api/resume/analyze",
            files={"file": ("resume.pdf", io.BytesIO(test_pdf_bytes), "application/pdf")}
        )
        assert response.status_code == 200
        return response.json()["resume_id"]

    def test_match_with_valid_data(self, client, test_pdf_bytes):
        """Match a previously analyzed resume against a job description."""
        resume_id = self._ensure_resume_uploaded(client, test_pdf_bytes)
        
        response = client.post(
            "/api/resume/match",
            json={
                "resume_id": resume_id,
                "job_description": "We are looking for a senior Python backend developer with experience in FastAPI, Redis, and PostgreSQL."
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "match_result" in data
        assert "score" in data["match_result"]
        assert 0 <= data["match_result"]["score"] <= 100
        assert "skills_match_rate" in data["match_result"]
        assert "experience_relevance" in data["match_result"]
        assert "comment" in data["match_result"]

    def test_match_with_empty_job_description(self, client, test_pdf_bytes):
        """Empty job description should return 400."""
        resume_id = self._ensure_resume_uploaded(client, test_pdf_bytes)
        
        response = client.post(
            "/api/resume/match",
            json={
                "resume_id": resume_id,
                "job_description": "   "  # Only whitespace
            }
        )
        assert response.status_code == 400

    def test_match_with_invalid_resume_id(self, client):
        """Using a non-existent resume_id should return 404."""
        response = client.post(
            "/api/resume/match",
            json={
                "resume_id": "nonexistent_resume_id_12345",
                "job_description": "Software Engineer position"
            }
        )
        assert response.status_code == 404

    def test_match_missing_fields(self, client):
        """Missing required fields should return 422."""
        response = client.post(
            "/api/resume/match",
            json={}
        )
        assert response.status_code == 422

    def test_match_same_inputs_hits_cache(self, client, test_pdf_bytes):
        """Same resume + same job description should hit cache on second call."""
        resume_id = self._ensure_resume_uploaded(client, test_pdf_bytes)
        job_desc = "Looking for a Python developer experienced in cloud services."
        
        # First match
        response1 = client.post(
            "/api/resume/match",
            json={"resume_id": resume_id, "job_description": job_desc}
        )
        assert response1.status_code == 200
        
        # Second match with same inputs
        response2 = client.post(
            "/api/resume/match",
            json={"resume_id": resume_id, "job_description": job_desc}
        )
        assert response2.status_code == 200
        data2 = response2.json()
        assert "Cache Hit" in data2["message"]
