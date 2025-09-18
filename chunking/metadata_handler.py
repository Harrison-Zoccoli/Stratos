from typing import Dict, Any, List
from datetime import datetime

class MetadataHandler:
    """
    Handles metadata collection and formatting for chunks.
    """
    
    def __init__(self):
        pass
    
    def create_chunk_metadata(self, chunk_id: int, chunk_text: str, 
                            source_page: int, start_pos: int, end_pos: int,
                            token_count: int, chunk_index: int, 
                            total_chunks: int) -> Dict[str, Any]:
        """
        Create metadata for a single chunk.
        
        Args:
            chunk_id: Unique chunk identifier
            chunk_text: The chunk text content
            source_page: Source page number
            start_pos: Start position in original text
            end_pos: End position in original text
            token_count: Number of tokens in chunk
            chunk_index: Index of chunk in sequence
            total_chunks: Total number of chunks
            
        Returns:
            Dictionary with chunk metadata
        """
        return {
            'chunk_id': chunk_id,
            'chunk_index': chunk_index,
            'total_chunks': total_chunks,
            'source_page': source_page,
            'start_position': start_pos,
            'end_position': end_pos,
            'text_length': len(chunk_text),
            'token_count': token_count,
            'created_at': datetime.now().isoformat(),
            'chunk_text_preview': chunk_text[:100] + "..." if len(chunk_text) > 100 else chunk_text
        }
    
    def create_chunking_summary(self, total_chunks: int, total_tokens: int, 
                              total_characters: int, chunk_size: int, 
                              overlap_size: int, source_pages: int) -> Dict[str, Any]:
        """
        Create summary metadata for the entire chunking process.
        
        Args:
            total_chunks: Total number of chunks created
            total_tokens: Total tokens across all chunks
            total_characters: Total characters across all chunks
            chunk_size: Target chunk size
            overlap_size: Overlap size used
            source_pages: Number of source pages
            
        Returns:
            Dictionary with chunking summary
        """
        return {
            'chunking_summary': {
                'total_chunks': total_chunks,
                'total_tokens': total_tokens,
                'total_characters': total_characters,
                'chunk_size': chunk_size,
                'overlap_size': overlap_size,
                'source_pages': source_pages,
                'average_tokens_per_chunk': total_tokens / total_chunks if total_chunks > 0 else 0,
                'average_characters_per_chunk': total_characters / total_chunks if total_chunks > 0 else 0,
                'created_at': datetime.now().isoformat()
            }
        }
    
    def format_chunk_for_output(self, chunk_id: int, chunk_text: str, 
                              metadata: Dict[str, Any]) -> str:
        """
        Format a chunk for text output with metadata.
        
        Args:
            chunk_id: Chunk identifier
            chunk_text: Chunk text content
            metadata: Chunk metadata
            
        Returns:
            Formatted chunk string
        """
        return f"=== CHUNK {chunk_id} ===\n" \
               f"Page: {metadata['source_page']} | " \
               f"Tokens: {metadata['token_count']} | " \
               f"Position: {metadata['start_position']}-{metadata['end_position']}\n" \
               f"{chunk_text}\n\n"