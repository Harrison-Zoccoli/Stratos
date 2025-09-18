import pdfplumber
import fitz  # PyMuPDF
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class PDFExtractor:
    """
    Handles PDF text extraction functionality with multiple extraction methods.
    """
    
    def __init__(self):
        pass
    
    def extract_text_from_pdf(self, pdf_path: str, method: str = "pdfplumber") -> List[Dict[str, Any]]:
        """
        Extract raw text from PDF pages using different methods.
        
        Args:
            pdf_path: Path to PDF file
            method: Extraction method ("pdfplumber" or "pymupdf")
            
        Returns:
            List of page dictionaries with raw text
        """
        logger.info(f"Extracting text from PDF: {pdf_path} using {method}")
        
        if method == "pdfplumber":
            return self._extract_with_pdfplumber(pdf_path)
        elif method == "pymupdf":
            return self._extract_with_pymupdf(pdf_path)
        else:
            raise ValueError(f"Unknown extraction method: {method}")
    
    def _extract_with_pdfplumber(self, pdf_path: str) -> List[Dict[str, Any]]:
        """Extract using pdfplumber (current method)."""
        pages = []
        with pdfplumber.open(pdf_path) as pdf:
            total_pages = len(pdf.pages)
            logger.info(f"Found {total_pages} pages in PDF (pdfplumber)")
            
            for page_num, page in enumerate(pdf.pages, 1):
                try:
                    raw_text = page.extract_text()
                    
                    page_data = {
                        'page_number': page_num,
                        'raw_text': raw_text or '',
                        'raw_length': len(raw_text) if raw_text else 0,
                        'extraction_method': 'pdfplumber'
                    }
                    
                    pages.append(page_data)
                    logger.info(f"Extracted page {page_num}: {page_data['raw_length']} characters")
                    
                except Exception as e:
                    logger.error(f"Error extracting page {page_num}: {e}")
                    pages.append({
                        'page_number': page_num,
                        'raw_text': '',
                        'raw_length': 0,
                        'extraction_method': 'pdfplumber',
                        'error': str(e)
                    })
        
        return pages
    
    def _extract_with_pymupdf(self, pdf_path: str) -> List[Dict[str, Any]]:
        """Extract using PyMuPDF (alternative method)."""
        try:
            import fitz
        except ImportError:
            logger.error("PyMuPDF not installed. Install with: pip install PyMuPDF")
            raise ImportError("PyMuPDF not available")
        
        pages = []
        doc = fitz.open(pdf_path)
        total_pages = len(doc)
        logger.info(f"Found {total_pages} pages in PDF (PyMuPDF)")
        
        for page_num in range(total_pages):
            try:
                page = doc[page_num]
                raw_text = page.get_text()
                
                page_data = {
                    'page_number': page_num + 1,
                    'raw_text': raw_text or '',
                    'raw_length': len(raw_text) if raw_text else 0,
                    'extraction_method': 'pymupdf'
                }
                
                pages.append(page_data)
                logger.info(f"Extracted page {page_num + 1}: {page_data['raw_length']} characters")
                
            except Exception as e:
                logger.error(f"Error extracting page {page_num + 1}: {e}")
                pages.append({
                    'page_number': page_num + 1,
                    'raw_text': '',
                    'raw_length': 0,
                    'extraction_method': 'pymupdf',
                    'error': str(e)
                })
        
        doc.close()
        return pages
    
    def get_extraction_summary(self, pages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Get summary of PDF extraction.
        
        Args:
            pages: List of extracted pages
            
        Returns:
            Summary dictionary
        """
        total_pages = len(pages)
        total_characters = sum(page.get('raw_length', 0) for page in pages)
        pages_with_errors = sum(1 for page in pages if 'error' in page)
        
        return {
            'total_pages': total_pages,
            'total_characters': total_characters,
            'pages_with_errors': pages_with_errors,
            'success_rate': (total_pages - pages_with_errors) / total_pages if total_pages > 0 else 0
        }