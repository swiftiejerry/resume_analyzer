import sys
import os

# Ensure the project root is in the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from fastapi.testclient import TestClient
from main import app


@pytest.fixture(scope="session")
def client():
    """FastAPI TestClient for integration tests."""
    return TestClient(app)


@pytest.fixture(scope="session")
def test_pdf_bytes():
    """Generate and return test PDF bytes."""
    from tests.generate_test_pdf import generate_test_resume_pdf
    import tempfile
    
    pdf_path = os.path.join(tempfile.gettempdir(), "test_resume_fixture.pdf")
    generate_test_resume_pdf(pdf_path)
    with open(pdf_path, "rb") as f:
        return f.read()


@pytest.fixture(scope="session")
def empty_pdf_bytes():
    """Generate and return empty PDF bytes."""
    from tests.generate_test_pdf import generate_empty_pdf
    import tempfile
    
    pdf_path = os.path.join(tempfile.gettempdir(), "test_empty_fixture.pdf")
    generate_empty_pdf(pdf_path)
    with open(pdf_path, "rb") as f:
        return f.read()
