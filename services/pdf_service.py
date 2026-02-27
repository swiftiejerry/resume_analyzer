import pdfplumber
import fitz  # PyMuPDF
import io
import base64
from typing import List

class PDFService:
    @staticmethod
    def extract_text(file_bytes: bytes) -> str:
        """
        Extract text from PDF file bytes.
        Tries pdfplumber first, falls back to PyMuPDF.
        If both return empty (image-based/vector PDF), returns empty string.
        """
        text = PDFService._extract_with_pdfplumber(file_bytes)
        if text and text.strip():
            return text
        
        # Fallback: try PyMuPDF
        text = PDFService._extract_with_pymupdf(file_bytes)
        if text and text.strip():
            return text
        
        return ""

    @staticmethod
    def _extract_with_pdfplumber(file_bytes: bytes) -> str:
        """Extract text using pdfplumber."""
        text_content = []
        try:
            with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_content.append(page_text)
            
            full_text = "\n".join(text_content)
            full_text = "\n".join([line.strip() for line in full_text.split("\n") if line.strip()])
            return full_text
        except Exception as e:
            print(f"pdfplumber extraction failed: {e}")
            return ""

    @staticmethod
    def _extract_with_pymupdf(file_bytes: bytes) -> str:
        """Extract text using PyMuPDF (fitz)."""
        text_content = []
        try:
            doc = fitz.open(stream=file_bytes, filetype="pdf")
            for page in doc:
                page_text = page.get_text()
                if page_text and page_text.strip():
                    text_content.append(page_text.strip())
            doc.close()
            
            full_text = "\n".join(text_content)
            full_text = "\n".join([line.strip() for line in full_text.split("\n") if line.strip()])
            return full_text
        except Exception as e:
            print(f"PyMuPDF extraction failed: {e}")
            return ""

    @staticmethod
    def is_image_based_pdf(file_bytes: bytes) -> bool:
        """Check if a PDF is image/vector-based (no extractable text)."""
        try:
            doc = fitz.open(stream=file_bytes, filetype="pdf")
            has_text = False
            for page in doc:
                if page.get_text().strip():
                    has_text = True
                    break
            doc.close()
            return not has_text
        except Exception:
            return False

    @staticmethod
    def pdf_pages_to_base64_images(file_bytes: bytes, dpi: int = 200) -> List[str]:
        """
        Convert PDF pages to base64-encoded PNG images.
        Used for image-based PDFs that need OCR/vision AI processing.
        Returns a list of base64-encoded image strings.
        """
        images = []
        try:
            doc = fitz.open(stream=file_bytes, filetype="pdf")
            for page in doc:
                # Render page to pixmap at given DPI
                mat = fitz.Matrix(dpi / 72, dpi / 72)
                pix = page.get_pixmap(matrix=mat)
                img_bytes = pix.tobytes("png")
                img_b64 = base64.b64encode(img_bytes).decode("utf-8")
                images.append(img_b64)
            doc.close()
        except Exception as e:
            print(f"PDF to image conversion failed: {e}")
        return images
