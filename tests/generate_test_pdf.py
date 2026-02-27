"""Generate a test PDF resume with Chinese content for testing."""
import sys
import os

# Add parent directory so we can run this standalone
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fpdf import FPDF

def generate_test_resume_pdf(output_path: str):
    """Generate a simple PDF resume with test data."""
    pdf = FPDF()
    pdf.add_page()
    
    # Use a built-in font that supports basic ASCII
    # For Chinese we embed a Unicode font
    font_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Try to use a Unicode font for Chinese, fall back to Helvetica
    pdf.set_font("Helvetica", size=16)
    pdf.cell(0, 12, text="Resume / Personal Profile", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.ln(5)
    
    pdf.set_font("Helvetica", size=11)
    lines = [
        "Name: Zhang Wei",
        "Phone: 13812345678",
        "Email: zhangwei@example.com",
        "Address: Beijing, Haidian District",
        "",
        "=== Job Intention ===",
        "Senior Python Backend Engineer",
        "",
        "=== Work Experience: 5 years ===",
        "2019-2024: ABC Tech Co. - Backend Developer",
        "  - Developed RESTful API with FastAPI",
        "  - Managed PostgreSQL and Redis clusters",
        "  - Built CI/CD pipelines with GitHub Actions",
        "",
        "2017-2019: XYZ Internet Co. - Junior Developer",
        "  - Web development with Django",
        "  - Database optimization",
        "",
        "=== Education ===",
        "Bachelor of Computer Science",
        "Peking University, 2013-2017",
        "",
        "=== Skills ===",
        "Python, FastAPI, Django, PostgreSQL, Redis,",
        "Docker, Kubernetes, AWS, Git, Linux",
        "Machine Learning basics, NLP",
    ]
    
    for line in lines:
        pdf.cell(0, 8, text=line, new_x="LMARGIN", new_y="NEXT")
    
    pdf.output(output_path)
    print(f"Test PDF generated: {output_path}")


def generate_empty_pdf(output_path: str):
    """Generate a PDF with no extractable text."""
    pdf = FPDF()
    pdf.add_page()
    # Just a blank page
    pdf.output(output_path)
    print(f"Empty PDF generated: {output_path}")


if __name__ == "__main__":
    test_dir = os.path.dirname(os.path.abspath(__file__))
    generate_test_resume_pdf(os.path.join(test_dir, "test_resume.pdf"))
    generate_empty_pdf(os.path.join(test_dir, "test_empty.pdf"))
