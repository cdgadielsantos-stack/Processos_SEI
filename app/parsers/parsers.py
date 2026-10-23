import os
import logging
from pathlib import Path
from typing import Optional

# Optional imports - we'll try to import and handle missing gracefully
try:
    import pdfplumber
except ImportError:
    pdfplumber = None

try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None

try:
    from docx import Document as DocxDocument
except ImportError:
    DocxDocument = None

try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None

try:
    import pytesseract
    from PIL import Image
except ImportError:
    pytesseract = None
    Image = None

logger = logging.getLogger(__name__)

class ParserService:
    def __init__(self, tesseract_cmd: Optional[str] = None):
        """
        Initialize the parser service.
        :param tesseract_cmd: Path to tesseract executable (if needed for OCR).
        """
        if tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
        # Check availability of libraries
        self._check_dependencies()

    def _check_dependencies(self):
        """Log warnings for missing optional dependencies."""
        if not pdfplumber and not fitz:
            logger.warning("Neither pdfplumber nor PyMuPDF available. PDF parsing will be limited.")
        if not DocxDocument:
            logger.warning("python-docx not available. DOCX parsing will be skipped.")
        if not BeautifulSoup:
            logger.warning("beautifulsoup4 not available. HTML parsing will be skipped.")
        if not pytesseract:
            logger.warning("pytesseract not available. OCR will be skipped.")

    def parse_file(self, file_path: Path) -> Optional[str]:
        """
        Parse a file and return extracted text.
        :param file_path: Path to the file.
        :return: Extracted text string or None if failed/unsupported.
        """
        if not file_path.exists():
            logger.error(f"File not found: {file_path}")
            return None

        suffix = file_path.suffix.lower()
        logger.info(f"Parsing file: {file_path} (type: {suffix})")

        try:
            if suffix == '.pdf':
                return self._parse_pdf(file_path)
            elif suffix == '.docx':
                return self._parse_docx(file_path)
            elif suffix in ['.html', '.htm']:
                return self._parse_html(file_path)
            elif suffix == '.txt':
                return self._parse_txt(file_path)
            else:
                # Try OCR as fallback for images or unknown types
                logger.info(f"Attempting OCR for unsupported type: {suffix}")
                return self._parse_ocr(file_path)
        except Exception as e:
            logger.exception(f"Error parsing file {file_path}: {e}")
            return None

    def _parse_pdf(self, file_path: Path) -> Optional[str]:
        """Parse PDF using pdfplumber or PyMuPDF."""
        text = ""
        # Try pdfplumber first
        if pdfplumber:
            try:
                with pdfplumber.open(file_path) as pdf:
                    for page in pdf.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n"
                if text.strip():
                    return text.strip()
            except Exception as e:
                logger.warning(f"pdfplumber failed: {e}, trying PyMuPDF")
        # Fallback to PyMuPDF
        if fitz:
            try:
                doc = fitz.open(file_path)
                for page_num in range(len(doc)):
                    page = doc.load_page(page_num)
                    text += page.get_text()
                doc.close()
                if text.strip():
                    return text.strip()
            except Exception as e:
                logger.error(f"PyMuPDF failed: {e}")
        return None if not text.strip() else text.strip()

    def _parse_docx(self, file_path: Path) -> Optional[str]:
        """Parse DOCX using python-docx."""
        if not DocxDocument:
            logger.error("python-docx not installed")
            return None
        try:
            doc = DocxDocument(file_path)
            text = []
            for para in doc.paragraphs:
                text.append(para.text)
            return '\n'.join(text)
        except Exception as e:
            logger.exception(f"Error reading DOCX {file_path}: {e}")
            return None

    def _parse_html(self, file_path: Path) -> Optional[str]:
        """Parse HTML using BeautifulSoup."""
        if not BeautifulSoup:
            logger.error("beautifulsoup4 not installed")
            return None
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            soup = BeautifulSoup(content, 'html.parser')
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            text = soup.get_text()
            # Clean up whitespace
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = '\n'.join(chunk for chunk in chunks if chunk)
            return text
        except Exception as e:
            logger.exception(f"Error parsing HTML {file_path}: {e}")
            return None

    def _parse_txt(self, file_path: Path) -> Optional[str]:
        """Parse plain text file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.exception(f"Error reading TXT file {file_path}: {e}")
            return None

    def _parse_ocr(self, file_path: Path) -> Optional[str]:
        """Perform OCR on image or PDF (if needed)."""
        if not pytesseract or not Image:
            logger.error("OCR dependencies not available (pytesseract, pillow)")
            return None
        try:
            # If PDF, convert to images first (requires pdf2image)
            # For simplicity, we assume file is an image
            img = Image.open(file_path)
            text = pytesseract.image_to_string(img, lang='por')  # Portuguese
            return text
        except Exception as e:
            logger.exception(f"OCR failed on {file_path}: {e}")
            return None