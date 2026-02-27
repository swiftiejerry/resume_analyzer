"""Unit tests for PDFService."""
import os
import pytest
from services.pdf_service import PDFService


class TestPDFServiceExtractText:
    """Tests for PDFService.extract_text"""

    def test_extract_text_from_valid_pdf(self, test_pdf_bytes):
        """Should extract text content from a valid PDF with text."""
        result = PDFService.extract_text(test_pdf_bytes)
        assert result is not None
        assert len(result) > 0
        # Verify some expected content is in the extracted text
        assert "Zhang Wei" in result
        assert "13812345678" in result
        assert "zhangwei@example.com" in result
        assert "Python" in result

    def test_extract_text_contains_work_experience(self, test_pdf_bytes):
        """Should extract work experience info."""
        result = PDFService.extract_text(test_pdf_bytes)
        assert "FastAPI" in result
        assert "Backend" in result

    def test_extract_text_from_empty_pdf(self, empty_pdf_bytes):
        """Should return empty string for a PDF with no text."""
        result = PDFService.extract_text(empty_pdf_bytes)
        assert result == "" or result is None or len(result.strip()) == 0

    def test_extract_text_with_invalid_bytes(self):
        """Should return empty string for non-PDF bytes (both parsers handle gracefully)."""
        invalid_bytes = b"This is not a PDF file content"
        result = PDFService.extract_text(invalid_bytes)
        assert result == ""

    def test_extract_text_with_empty_bytes(self):
        """Should return empty string for empty bytes."""
        result = PDFService.extract_text(b"")
        assert result == ""


class TestPDFServiceImageDetection:
    """Tests for PDFService.is_image_based_pdf and pdf_pages_to_base64_images"""

    def test_text_pdf_not_image_based(self, test_pdf_bytes):
        """A text-based PDF should not be detected as image-based."""
        assert PDFService.is_image_based_pdf(test_pdf_bytes) == False

    def test_empty_pdf_is_image_based(self, empty_pdf_bytes):
        """An empty PDF (no text) is detected as image-based."""
        assert PDFService.is_image_based_pdf(empty_pdf_bytes) == True

    def test_pdf_to_images(self, test_pdf_bytes):
        """Should convert PDF pages to base64 images."""
        images = PDFService.pdf_pages_to_base64_images(test_pdf_bytes, dpi=72)
        assert len(images) > 0
        # Each image should be a valid base64 string
        import base64
        for img in images:
            decoded = base64.b64decode(img)
            assert len(decoded) > 0
            # PNG header starts with \x89PNG
            assert decoded[:4] == b'\x89PNG'

    def test_invalid_bytes_to_images(self):
        """Should return empty list for invalid bytes."""
        result = PDFService.pdf_pages_to_base64_images(b"not a pdf")
        assert result == []
