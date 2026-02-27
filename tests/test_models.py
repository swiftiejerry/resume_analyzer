"""Unit tests for Pydantic data models."""
import pytest
from models.resume import BasicInfo, ResumeData, ResumeAnalyzeResponse, JobDescriptionRequest, MatchResult, ResumeMatchResponse


class TestBasicInfo:
    def test_all_fields_provided(self):
        info = BasicInfo(name="Zhang Wei", phone="13812345678", email="test@test.com", address="Beijing")
        assert info.name == "Zhang Wei"
        assert info.phone == "13812345678"

    def test_all_fields_optional(self):
        info = BasicInfo()
        assert info.name is None
        assert info.phone is None
        assert info.email is None
        assert info.address is None

    def test_partial_fields(self):
        info = BasicInfo(name="Test User")
        assert info.name == "Test User"
        assert info.phone is None


class TestResumeData:
    def test_full_construction(self):
        data = ResumeData(
            basic_info=BasicInfo(name="Test"),
            job_intention="Engineer",
            work_years="5 years",
            education_background="Master",
            raw_text_summary="Experienced developer"
        )
        assert data.basic_info.name == "Test"
        assert data.job_intention == "Engineer"

    def test_minimal_construction(self):
        data = ResumeData(basic_info=BasicInfo())
        assert data.job_intention is None
        assert data.work_years is None

    def test_model_dump_and_reconstruct(self):
        """Test serialization round-trip."""
        original = ResumeData(
            basic_info=BasicInfo(name="RoundTrip", email="rt@test.com"),
            job_intention="PM",
            work_years="3"
        )
        dumped = original.model_dump()
        reconstructed = ResumeData(**dumped)
        assert reconstructed.basic_info.name == "RoundTrip"
        assert reconstructed.job_intention == "PM"


class TestJobDescriptionRequest:
    def test_valid_request(self):
        req = JobDescriptionRequest(resume_id="abc123", job_description="Looking for Python developer")
        assert req.resume_id == "abc123"
        assert "Python" in req.job_description

    def test_missing_fields_raises_error(self):
        with pytest.raises(Exception):
            JobDescriptionRequest()  # Both fields are required


class TestMatchResult:
    def test_valid_construction(self):
        result = MatchResult(score=85, skills_match_rate="85%", experience_relevance="High", comment="Good fit")
        assert result.score == 85
        assert result.comment == "Good fit"

    def test_model_dump_and_reconstruct(self):
        original = MatchResult(score=70, skills_match_rate="60%", experience_relevance="Medium", comment="OK")
        dumped = original.model_dump()
        reconstructed = MatchResult(**dumped)
        assert reconstructed.score == 70


class TestResumeAnalyzeResponse:
    def test_valid_response(self):
        resp = ResumeAnalyzeResponse(
            resume_id="hash123",
            data=ResumeData(basic_info=BasicInfo(name="Test")),
            message="Success"
        )
        assert resp.resume_id == "hash123"
        assert resp.data.basic_info.name == "Test"
        assert resp.message == "Success"


class TestResumeMatchResponse:
    def test_valid_response(self):
        resp = ResumeMatchResponse(
            resume_id="hash123",
            match_result=MatchResult(score=90, skills_match_rate="90%", experience_relevance="Very High", comment="Excellent"),
            message="Success"
        )
        assert resp.resume_id == "hash123"
        assert resp.match_result.score == 90
