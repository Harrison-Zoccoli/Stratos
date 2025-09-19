import json
from pathlib import Path
from typing import Dict, Any, List
from .batch_processor import BatchProcessor
from .storage_handler import StorageHandler
from .config import EmbeddingConfig

class EmbeddingProcessor:
    """
    Main class for processing chunks into embeddings.
    """
    
    def __init__(self):
        self.batch_processor = BatchProcessor()
        self.storage_handler = StorageHandler()
    
    def process_pdf_embeddings(self, chunks_metadata: List[Dict[str, Any]], pdf_name: str) -> Dict[str, Any]:
        """
        Process all chunks for a PDF into embeddings.
        
        Args:
            chunks_metadata: List of chunk dictionaries (from chunking results)
            pdf_name: Name of the PDF (without extension)
            
        Returns:
            Dictionary with processing results
        """
        print(f"Starting embedding processing for: {pdf_name}")
        print(f"Batch size: {EmbeddingConfig.BATCH_SIZE}")
        
        if not chunks_metadata:
            print("No chunks found to process")
            return {}
        
        # Process chunks in batches
        processed_chunks = self.batch_processor.process_all_batches(chunks_metadata)
        
        if not processed_chunks:
            print("No chunks were successfully processed")
            return {}
        
        # Generate summary
        summary = self.storage_handler.get_embeddings_summary(processed_chunks)
        
        # Save embeddings
        saved_files = self.storage_handler.save_embeddings(processed_chunks, pdf_name, summary)
        
        print(f"Embedding processing complete for {pdf_name}")
        print(f"Processed: {len(processed_chunks)}/{len(chunks_metadata)} chunks")
        print(f"Embedding dimension: {summary.get('embedding_dimension', 'Unknown')}")
        
        return {
            'pdf_name': pdf_name,
            'processed_chunks': len(processed_chunks),
            'total_chunks': len(chunks_metadata),
            'summary': summary,
            'saved_files': saved_files
        } 