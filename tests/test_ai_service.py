"""Unit tests for AIService._parse_json_result (JSON parsing logic only, no API calls)."""
import pytest
from services.ai_service import AIService


class TestParseJsonResult:
    """Tests for AIService._parse_json_result static method."""

    def test_parse_clean_json(self):
        """Should parse a clean JSON string."""
        text = '{"score": 85, "comment": "Good match"}'
        result = AIService._parse_json_result(text)
        assert result["score"] == 85
        assert result["comment"] == "Good match"

    def test_parse_json_with_markdown_json_block(self):
        """Should strip ```json ... ``` wrapper and parse correctly."""
        text = '```json\n{"name": "Zhang Wei", "skills": ["Python", "FastAPI"]}\n```'
        result = AIService._parse_json_result(text)
        assert result["name"] == "Zhang Wei"
        assert "Python" in result["skills"]

    def test_parse_json_with_plain_markdown_block(self):
        """Should strip ``` ... ``` wrapper and parse correctly."""
        text = '```\n{"name": "Test"}\n```'
        result = AIService._parse_json_result(text)
        assert result["name"] == "Test"

    def test_parse_json_with_leading_trailing_text(self):
        """Should extract JSON from text with surrounding non-JSON content."""
        text = 'Here is the result: {"score": 90, "comment": "Excellent"} Hope this helps!'
        result = AIService._parse_json_result(text)
        assert result["score"] == 90
        assert result["comment"] == "Excellent"

    def test_parse_completely_invalid_text(self):
        """Should return empty dict for completely non-JSON text."""
        text = "No JSON here at all, just plain text."
        result = AIService._parse_json_result(text)
        assert result == {}

    def test_parse_empty_string(self):
        """Should return empty dict for empty string."""
        result = AIService._parse_json_result("")
        assert result == {}

    def test_parse_nested_json(self):
        """Should correctly parse nested JSON structures."""
        text = '{"basic_info": {"name": "Li Ming", "phone": "13900001111"}, "job_intention": "Engineer"}'
        result = AIService._parse_json_result(text)
        assert result["basic_info"]["name"] == "Li Ming"
        assert result["job_intention"] == "Engineer"

    def test_parse_json_with_unicode(self):
        """Should handle Chinese/Unicode content in JSON."""
        text = '{"name": "张伟", "comment": "技能匹配度高"}'
        result = AIService._parse_json_result(text)
        assert result["name"] == "张伟"
        assert "技能" in result["comment"]

    def test_parse_json_with_whitespace(self):
        """Should handle JSON with extra whitespace."""
        text = '   \n  {"score": 75}  \n  '
        result = AIService._parse_json_result(text)
        assert result["score"] == 75
