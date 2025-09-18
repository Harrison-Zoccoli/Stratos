"""
Input processing package for PDF text extraction and normalization.
"""

from typing import Dict, Any, List

class SummaryGenerator:
    """
    Generates processing summaries and statistics.
    """
    
    def __init__(self):
        pass
    
    def generate_final_summary(self, extraction_summary: Dict[str, Any], normalized_pages: List[Dict[str, Any]], normalizer) -> Dict[str, Any]:
        """
        Generate final processing summary.
        
        Args:
            extraction_summary: Summary from PDF extraction
            normalized_pages: List of normalized pages
            normalizer: Normalizer instance for stats
            
        Returns:
            Final summary dictionary
        """
        total_pages = len(normalized_pages)
        total_normalized_length = sum(page.get('normalized_length', 0) for page in normalized_pages)
        total_words = sum(page.get('word_count', 0) for page in normalized_pages)
        total_tokens = sum(page.get('token_estimate', 0) for page in normalized_pages)
        
        # Get normalization stats
        norm_results = [{
            'normalized_text': page.get('normalized_text', ''),
            'original_length': page.get('raw_length', 0),
            'normalized_length': page.get('normalized_length', 0),
            'word_count': page.get('word_count', 0),
            'token_estimate': page.get('token_estimate', 0),
            'transformations_applied': page.get('transformations_applied', [])
        } for page in normalized_pages]
        
        norm_stats = normalizer.get_normalization_stats(norm_results)
        
        return {
            'total_pages': total_pages,
            'total_raw_characters': extraction_summary['total_characters'],
            'total_normalized_characters': total_normalized_length,
            'total_words': total_words,
            'total_estimated_tokens': total_tokens,
            'compression_ratio': total_normalized_length / extraction_summary['total_characters'] if extraction_summary['total_characters'] > 0 else 0,
            'average_words_per_page': total_words / total_pages if total_pages > 0 else 0,
            'normalization_stats': norm_stats
        }
    
    def print_summary(self, results: Dict[str, Any]):
        """
        Print a formatted summary of the processing results.
        
        Args:
            results: Processing results dictionary
        """
        final_summary = results['final_summary']
        
        print("\n" + "="*60)
        print("PDF PROCESSING SUMMARY")
        print("="*60)
        print(f"PDF: {results['pdf_path']}")
        print(f"Total pages: {final_summary['total_pages']}")
        print(f"Total raw characters: {final_summary['total_raw_characters']:,}")
        print(f"Total normalized characters: {final_summary['total_normalized_characters']:,}")
        print(f"Compression ratio: {final_summary['compression_ratio']:.2%}")
        print(f"Total words: {final_summary['total_words']:,}")
        print(f"Estimated tokens: {final_summary['total_estimated_tokens']:,}")
        print(f"Average words per page: {final_summary['average_words_per_page']:.0f}")
        
        # Show normalization stats
        norm_stats = final_summary['normalization_stats']
        print(f"\nNormalization Statistics:")
        print(f"  Total texts processed: {norm_stats['total_texts']}")
        print(f"  Transformations applied:")
        for trans, count in norm_stats['transformation_counts'].items():
            print(f"    - {trans}: {count}")
    
    def print_preview(self, results: Dict[str, Any], preview_length: int = 300):
        """
        Print a preview of the first page.
        
        Args:
            results: Processing results dictionary
            preview_length: Number of characters to show in preview
        """
        if results['pages']:
            first_page = results['pages'][0]
            print(f"\nFirst page preview (first {preview_length} chars):")
            print("-" * 50)
            print(first_page['normalized_text'][:preview_length] + "...") 