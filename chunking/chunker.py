import re
from typing import List, Dict, Any
from .token_counter import TokenCounter
from .metadata_handler import MetadataHandler

# Configuration - easily changeable
CHUNK_SIZE = 1000
OVERLAP_SIZE = 150

class Chunker:
    """
    Handles text chunking with configurable size and overlap.
    """
    
    def __init__(self):
        self.chunk_size = CHUNK_SIZE
        self.overlap_size = OVERLAP_SIZE
        self.token_counter = TokenCounter()
        self.metadata_handler = MetadataHandler()
    
    def chunk_pages(self, normalized_pages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Chunk normalized pages into smaller pieces with proper overlap across pages.
        
        Args:
            normalized_pages: List of normalized page dictionaries
            
        Returns:
            Dictionary with chunks, metadata, and summary
        """
        all_chunks = []
        chunk_metadata = []
        chunk_id = 1
        global_char_position = 0
        carryover_text = ""  # Text to carry over from previous page
        
        for page in normalized_pages:
            page_text = page.get('normalized_text', '')
            page_number = page.get('page_number', 0)
            
            if not page_text.strip():
                continue
            
            # Combine carryover text with current page text
            combined_text = carryover_text + page_text
            if carryover_text:
                print(f"Carrying over {len(carryover_text)} characters from previous page to page {page_number}")
            
            # Chunk this combined text
            page_result = self._chunk_text(
                combined_text, 
                page_number, 
                chunk_id, 
                global_char_position - len(carryover_text)  # Adjust for carryover
            )
            
            all_chunks.extend(page_result['chunks'])
            chunk_metadata.extend(page_result['metadata'])
            
            # Get carryover text for next page
            carryover_text = page_result.get('carryover_text', '')
            
            # Update global position and chunk_id
            global_char_position += len(page_text)
            chunk_id += len(page_result['chunks'])
        
        # Update total_chunks in all metadata
        total_chunks = len(all_chunks)
        for metadata in chunk_metadata:
            metadata['total_chunks'] = total_chunks
        
        # Create summary
        total_tokens = sum(chunk['token_count'] for chunk in chunk_metadata)
        total_characters = sum(chunk['text_length'] for chunk in chunk_metadata)
        
        summary = self.metadata_handler.create_chunking_summary(
            total_chunks=total_chunks,
            total_tokens=total_tokens,
            total_characters=total_characters,
            chunk_size=self.chunk_size,
            overlap_size=self.overlap_size,
            source_pages=len(normalized_pages)
        )
        
        print(f"Created {total_chunks} chunks with {total_tokens:,} total tokens")
        
        return {
            'chunks': all_chunks,
            'metadata': chunk_metadata,
            'summary': summary
        }
    
    def _chunk_text(self, text: str, page_number: int, start_chunk_id: int, global_start_pos: int) -> Dict[str, Any]:
        """
        Chunk a single text into smaller pieces.
        
        Args:
            text: Text to chunk
            page_number: Source page number
            start_chunk_id: Starting chunk ID
            global_start_pos: Global character position in document
            
        Returns:
            Dictionary with chunks, metadata, and carryover text
        """
        chunks = []
        metadata = []
        chunk_id = start_chunk_id
        chunk_index = chunk_id - 1  # Global chunk index (0-based)
        
        # Split text into sentences first
        sentences = self._split_into_sentences(text)
        
        current_chunk = ""
        current_tokens = 0
        local_start_pos = 0  # Position within this page's text
        
        for i, sentence in enumerate(sentences):
            sentence_tokens = self.token_counter.count_tokens(sentence)
            
            # If adding this sentence would exceed chunk size, finalize current chunk
            if current_tokens + sentence_tokens > self.chunk_size and current_chunk:
                # Create chunk
                chunk_text = current_chunk.strip()
                local_end_pos = local_start_pos + len(chunk_text)
                global_end_pos = global_start_pos + local_end_pos
                
                chunk_metadata = self.metadata_handler.create_chunk_metadata(
                    chunk_id=chunk_id,
                    chunk_text=chunk_text,
                    source_page=page_number,
                    start_pos=global_start_pos + local_start_pos,  # Global position
                    end_pos=global_end_pos,  # Global position
                    token_count=current_tokens,
                    chunk_index=chunk_index,
                    total_chunks=0  # Will be updated later
                )
                
                chunks.append(chunk_text)
                metadata.append(chunk_metadata)
                
                # Start new chunk with overlap
                overlap_text = self._get_overlap_text(current_chunk)
                current_chunk = overlap_text
                current_tokens = self.token_counter.count_tokens(current_chunk)
                local_start_pos = local_end_pos - len(overlap_text)
                chunk_id += 1
                chunk_index += 1
            
            # Add sentence to current chunk
            current_chunk += sentence
            current_tokens += sentence_tokens
        
        # Handle remaining text
        if current_chunk.strip():
            chunk_text = current_chunk.strip()
            local_end_pos = local_start_pos + len(chunk_text)
            global_end_pos = global_start_pos + local_end_pos
            
            chunk_metadata = self.metadata_handler.create_chunk_metadata(
                chunk_id=chunk_id,
                chunk_text=chunk_text,
                source_page=page_number,
                start_pos=global_start_pos + local_start_pos,  # Global position
                end_pos=global_end_pos,  # Global position
                token_count=current_tokens,
                chunk_index=chunk_index,
                total_chunks=0  # Will be updated later
            )
            
            chunks.append(chunk_text)
            metadata.append(chunk_metadata)
        
        # Get carryover text for next page (overlap from last chunk)
        carryover_text = self._get_overlap_text(current_chunk) if current_chunk else ""
        
        return {
            'chunks': chunks,
            'metadata': metadata,
            'carryover_text': carryover_text
        }
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """
        Split text into sentences based on punctuation.
        
        Args:
            text: Text to split
            
        Returns:
            List of sentences
        """
        # Split on sentence-ending punctuation
        sentences = re.split(r'[.!?]+', text)
        
        # Clean up and filter empty sentences
        cleaned_sentences = []
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence:
                # Add back the punctuation if it was removed
                if not sentence.endswith(('.', '!', '?')):
                    sentence += '.'
                cleaned_sentences.append(sentence)
        
        return cleaned_sentences
    
    def _get_overlap_text(self, chunk_text: str) -> str:
        """
        Get overlap text from the end of a chunk.
        
        Args:
            chunk_text: The chunk text to get overlap from
            
        Returns:
            Overlap text
        """
        if not chunk_text:
            return ""
        
        # Split into sentences and take last few sentences that fit in overlap size
        sentences = self._split_into_sentences(chunk_text)
        overlap_text = ""
        
        # Start from the end and work backwards
        for sentence in reversed(sentences):
            test_overlap = sentence + " " + overlap_text
            if self.token_counter.count_tokens(test_overlap) <= self.overlap_size:
                overlap_text = test_overlap
            else:
                break
        
        return overlap_text.strip()
    
    def format_chunks_for_output(self, chunks: List[str], metadata: List[Dict[str, Any]]) -> str:
        """
        Format chunks for text output with headers.
        
        Args:
            chunks: List of chunk texts
            metadata: List of chunk metadata
            
        Returns:
            Formatted text string
        """
        output = []
        
        for i, (chunk, meta) in enumerate(zip(chunks, metadata)):
            header = f"=== CHUNK {meta['chunk_id']} ==="
            page_info = f"Page: {meta['source_page']} | Tokens: {meta['token_count']} | Position: {meta['start_position']}-{meta['end_position']}"
            
            output.append(header)
            output.append(page_info)
            output.append(chunk)
            output.append("")  # Empty line between chunks
        
        return "\n".join(output) 