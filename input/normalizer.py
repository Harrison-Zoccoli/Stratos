import re
import string
from typing import List, Dict, Any, Tuple
import logging

logger = logging.getLogger(__name__)

class TextNormalizer:
    """
    Conservative text normalizer that preserves meaning while fixing spacing issues.
    """
    
    def __init__(self):
        # Common patterns to remove for cleaner embeddings
        self.header_footer_patterns = [
            r'^\d+\s*$',  # Standalone page numbers
            r'^Page \d+ of \d+$',  # Page X of Y
            r'^Chapter \d+$',  # Chapter headers
            r'^Section \d+$',  # Section headers
            r'^Table of Contents$',  # TOC headers
            r'^Index$',  # Index headers
        ]
    
    def normalize_text(self, text: str, preserve_structure: bool = True) -> Dict[str, Any]:
        """
        Conservative normalization that preserves meaning while fixing spacing.
        """
        if not text or not text.strip():
            return {
                'normalized_text': '',
                'original_length': 0,
                'normalized_length': 0,
                'transformations_applied': [],
                'word_count': 0,
                'token_estimate': 0
            }
        
        original_text = text
        transformations = []
        
        # Step 1: Basic cleaning (only remove truly problematic characters)
        text = self._basic_cleaning(text, transformations)
        
        # Step 2: Remove headers/footers
        text = self._remove_headers_footers(text, transformations)
        
        # Step 3: Fix word spacing (the main issue)
        text = self._fix_word_spacing(text, transformations)
        
        # Step 4: Normalize whitespace
        text = self._normalize_whitespace(text, transformations)
        
        # Step 5: Preserve important structure if requested
        if preserve_structure:
            text = self._preserve_structure(text, transformations)
        
        # Step 6: Final cleanup
        text = self._final_cleanup(text, transformations)
        
        # Calculate metrics
        word_count = len(text.split())
        token_estimate = int(word_count * 1.3)
        
        return {
            'normalized_text': text,
            'original_length': len(original_text),
            'normalized_length': len(text),
            'transformations_applied': transformations,
            'word_count': word_count,
            'token_estimate': token_estimate
        }
    
    def _basic_cleaning(self, text: str, transformations: List[str]) -> str:
        """Remove only truly problematic characters."""
        # Remove null bytes and control characters (these are definitely artifacts)
        text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', text)
        
        # Normalize line endings
        text = text.replace('\r\n', '\n').replace('\r', '\n')
        
        # Remove excessive newlines (more than 2 consecutive)
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        transformations.append('basic_cleaning')
        return text
    
    def _remove_headers_footers(self, text: str, transformations: List[str]) -> str:
        """Remove common headers, footers, and page artifacts."""
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            
            # Skip empty lines
            if not line:
                cleaned_lines.append('')
                continue
            
            # Check against header/footer patterns
            is_header_footer = False
            for pattern in self.header_footer_patterns:
                if re.match(pattern, line, re.IGNORECASE):
                    is_header_footer = True
                    break
            
            # Skip if it's a header/footer
            if not is_header_footer:
                cleaned_lines.append(line)
        
        transformations.append('remove_headers_footers')
        return '\n'.join(cleaned_lines)
    
    def _fix_word_spacing(self, text: str, transformations: List[str]) -> str:
        """
        Fix word spacing issues while preserving all characters.
        This is the key fix for the embedding quality.
        """
        # Fix the main issue: lowercase letter followed by uppercase letter
        # This handles cases like "BySunTzu" -> "By Sun Tzu"
        text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)
        
        # Fix: word followed by comma without space (but keep comma attached to word)
        # "word," is correct, "word ," is not
        # This is already correct in most cases
        
        # Fix: period followed by uppercase letter (sentence boundary)
        text = re.sub(r'(\.)([A-Z])', r'\1 \2', text)
        
        # Fix: number followed by word
        text = re.sub(r'(\d)([A-Za-z])', r'\1 \2', text)
        
        # Fix: word followed by number  
        text = re.sub(r'([A-Za-z])(\d)', r'\1 \2', text)
        
        # Fix: punctuation followed by word (but preserve the punctuation)
        text = re.sub(r'([.!?;:])([A-Za-z])', r'\1 \2', text)
        
        transformations.append('fix_word_spacing')
        return text
    
    def _normalize_whitespace(self, text: str, transformations: List[str]) -> str:
        """Normalize whitespace while preserving text structure."""
        # Replace multiple spaces/tabs with single space
        text = re.sub(r'[ \t]+', ' ', text)
        
        # Remove leading/trailing whitespace from each line
        lines = [line.strip() for line in text.split('\n')]
        
        # Remove empty lines at start and end
        while lines and not lines[0]:
            lines.pop(0)
        while lines and not lines[-1]:
            lines.pop()
        
        transformations.append('normalize_whitespace')
        return '\n'.join(lines)
    
    def _preserve_structure(self, text: str, transformations: List[str]) -> str:
        """Preserve important document structure."""
        lines = text.split('\n')
        structured_lines = []
        
        for line in lines:
            # Preserve ALL CAPS headers
            if re.match(r'^[A-Z][A-Z\s]{3,}$', line.strip()):
                structured_lines.append(f"HEADER: {line.strip()}")
            else:
                structured_lines.append(line)
        
        transformations.append('preserve_structure')
        return '\n'.join(structured_lines)
    
    def _final_cleanup(self, text: str, transformations: List[str]) -> str:
        """Final cleanup while preserving meaning."""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Ensure text ends properly
        text = text.strip()
        
        # Only add period if text doesn't end with any punctuation
        if text and not text[-1] in '.!?;:':
            text += '.'
        
        transformations.append('final_cleanup')
        return text
    
    def normalize_batch(self, texts: List[str]) -> List[Dict[str, Any]]:
        """Normalize a batch of texts."""
        results = []
        for i, text in enumerate(texts):
            try:
                result = self.normalize_text(text)
                result['batch_index'] = i
                results.append(result)
            except Exception as e:
                logger.error(f"Error normalizing text at index {i}: {e}")
                results.append({
                    'normalized_text': '',
                    'original_length': len(text) if text else 0,
                    'normalized_length': 0,
                    'transformations_applied': ['error'],
                    'word_count': 0,
                    'token_estimate': 0,
                    'batch_index': i,
                    'error': str(e)
                })
        
        return results
    
    def get_normalization_stats(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get normalization statistics."""
        if not results:
            return {}
        
        total_original = sum(r.get('original_length', 0) for r in results)
        total_normalized = sum(r.get('normalized_length', 0) for r in results)
        total_words = sum(r.get('word_count', 0) for r in results)
        total_tokens = sum(r.get('token_estimate', 0) for r in results)
        
        # Count transformation types
        all_transformations = []
        for result in results:
            all_transformations.extend(result.get('transformations_applied', []))
        
        transformation_counts = {}
        for trans in all_transformations:
            transformation_counts[trans] = transformation_counts.get(trans, 0) + 1
        
        return {
            'total_texts': len(results),
            'total_original_length': total_original,
            'total_normalized_length': total_normalized,
            'compression_ratio': total_normalized / total_original if total_original > 0 else 0,
            'total_words': total_words,
            'total_estimated_tokens': total_tokens,
            'average_words_per_text': total_words / len(results) if results else 0,
            'transformation_counts': transformation_counts
        } 