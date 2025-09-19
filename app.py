import json
from pathlib import Path
from typing import Dict, Any, List

# Import our helper modules
from input.pdf_extractor import PDFExtractor
from input.normalizer import TextNormalizer
from input.summary_generator import SummaryGenerator
from chunking.chunker import Chunker
from embeddings.embedding_processor import EmbeddingProcessor

class PDFProcessor:
    """
    Main application class that orchestrates PDF processing and text normalization.
    Main entry point function first step
    """
    
    def __init__(self):
        self.pdf_extractor = PDFExtractor()
        self.normalizer = TextNormalizer()
        self.summary_generator = SummaryGenerator()
        self.chunker = Chunker()
        self.embedding_processor = EmbeddingProcessor()
    
    def process_pdf(self, pdf_path: str) -> Dict[str, Any]:
        """
        Main function to process a PDF file, rn a hardcoded file path can sub out later for better modularity
        """
        if not Path(pdf_path).exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        print(f"Processing PDF: {pdf_path}")
        
        # Extract text from PDF
        raw_pages = self.pdf_extractor.extract_text_from_pdf(pdf_path)
        extraction_summary = self.pdf_extractor.get_extraction_summary(raw_pages)
        
        # Normalize text
        normalized_pages = self._normalize_pages(raw_pages)
        
        # Generate final summary
        final_summary = self.summary_generator.generate_final_summary(
            extraction_summary, normalized_pages, self.normalizer
        )
        
        # Chunk the text
        chunking_results = self.chunker.chunk_pages(normalized_pages)
        
        # Process embeddings
        print("Generating embeddings...")
        pdf_name = Path(pdf_path).stem
        
        embedding_result = self.embedding_processor.process_pdf_embeddings(
            chunking_results['metadata'], pdf_name
        )
        
        print(f"Processing complete. Processed {len(normalized_pages)} pages")
        
        return {
            'pdf_path': pdf_path,
            'extraction_summary': extraction_summary,
            'final_summary': final_summary,
            'pages': normalized_pages,
            'chunking_results': chunking_results,
            'embedding_results': embedding_result
        }
    
    def _normalize_pages(self, raw_pages: list) -> list:
        """Normalize text from all pages."""
        print("Normalizing text...")
        
        # Extract just the text for batch processing
        texts = [page['raw_text'] for page in raw_pages]
        
        # Normalize in batch
        normalized_results = self.normalizer.normalize_batch(texts)
        
        # Combine with original page data
        normalized_pages = []
        for i, (raw_page, norm_result) in enumerate(zip(raw_pages, normalized_results)):
            normalized_page = {
                **raw_page,
                'normalized_text': norm_result['normalized_text'],
                'normalized_length': norm_result['normalized_length'],
                'word_count': norm_result['word_count'],
                'token_estimate': norm_result['token_estimate'],
                'transformations_applied': norm_result['transformations_applied']
            }
            
            if 'error' in norm_result:
                normalized_page['normalization_error'] = norm_result['error']
            
            normalized_pages.append(normalized_page)
        
        return normalized_pages
    
    def save_results(self, results: Dict[str, Any], output_dir: str = "."):
        """
        Save the essential files: normalized text, summary, chunked text, and chunk metadata.
        """
        output_path = Path(output_dir)
        pdf_name = Path(results['pdf_path']).stem
        
        # Save normalized text
        text_file = output_path / f"{pdf_name}_normalized.txt"
        with open(text_file, 'w', encoding='utf-8') as f:
            for page in results['pages']:
                f.write(f"=== PAGE {page['page_number']} ===\n")
                f.write(page['normalized_text'])
                f.write("\n\n")
        
        # Save summary
        summary_file = output_path / f"{pdf_name}_summary.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(results['final_summary'], f, indent=2, ensure_ascii=False)
        
        # Save chunked text
        chunked_file = output_path / f"{pdf_name}_chunked.txt"
        chunked_text = self.chunker.format_chunks_for_output(
            results['chunking_results']['chunks'],
            results['chunking_results']['metadata']
        )
        with open(chunked_file, 'w', encoding='utf-8') as f:
            f.write(chunked_text)
        
        # Save chunk metadata
        chunks_metadata_file = output_path / f"{pdf_name}_chunks_metadata.json"
        with open(chunks_metadata_file, 'w', encoding='utf-8') as f:
            json.dump({
                'chunks': results['chunking_results']['metadata'],
                'summary': results['chunking_results']['summary']
            }, f, indent=2, ensure_ascii=False)
        
        print(f"Results saved to:")
        print(f"  - Normalized text: {text_file}")
        print(f"  - Summary: {summary_file}")
        print(f"  - Chunked text: {chunked_file}")
        print(f"  - Chunk metadata: {chunks_metadata_file}")

def main():
    """
    Main function to run the PDF processor.
    """
    # Configuration
    pdf_path = "exampleStarbucks.pdf"
    
    try:
        # Initialize processor
        processor = PDFProcessor()
        
        # Process PDF
        results = processor.process_pdf(pdf_path)
        
        # Print summary using the helper
        processor.summary_generator.print_summary(results)
        
        # Save results
        processor.save_results(results)
        
        # Show preview using the helper
        processor.summary_generator.print_preview(results)
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main() 