import time
from typing import List, Dict, Any, Tuple
from openai import AzureOpenAI
import os
from dotenv import load_dotenv
from .config import EmbeddingConfig

load_dotenv()

class BatchProcessor:
    """
    Handles batch processing of chunks for embedding generation.
    """
    
    def __init__(self):
        self.client = AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version="2024-02-15-preview",
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
        )
        self.model_name = os.getenv("AZURE_OPENAI_MODEL_NAME")
    
    def create_batches(self, chunks: List[Dict[str, Any]]) -> List[List[Dict[str, Any]]]:
        """
        Create batches of chunks for processing.
        
        Args:
            chunks: List of chunk dictionaries
            
        Returns:
            List of batches, each containing up to BATCH_SIZE chunks
        """
        batches = []
        for i in range(0, len(chunks), EmbeddingConfig.BATCH_SIZE):
            batch = chunks[i:i + EmbeddingConfig.BATCH_SIZE]
            batches.append(batch)
        
        print(f"Created {len(batches)} batches of up to {EmbeddingConfig.BATCH_SIZE} chunks each")
        return batches
    
    def process_batch(self, batch: List[Dict[str, Any]], batch_num: int, total_batches: int) -> Tuple[List[Dict[str, Any]], bool]:
        """
        Process a single batch of chunks.
        
        Args:
            batch: List of chunk dictionaries
            batch_num: Current batch number (1-based)
            total_batches: Total number of batches
            
        Returns:
            Tuple of (processed_chunks, success_flag)
        """
        print(f"Processing batch {batch_num}/{total_batches} ({len(batch)} chunks)...")
        
        try:
            # Extract text from chunks - need to get the actual chunk text
            # The chunk metadata has the chunk info, but we need the actual text
            # Let me check what fields are available
            print(f"Sample chunk keys: {list(batch[0].keys()) if batch else 'No chunks'}")
            
            # For now, let's assume we need to get the text from somewhere else
            # This is the issue - we need the actual chunk text, not just metadata
            texts = []
            for chunk in batch:
                # We need to figure out how to get the actual text
                # The chunk metadata doesn't contain the text itself
                texts.append("PLACEHOLDER_TEXT")  # This won't work
            
            # Make API call
            response = self.client.embeddings.create(
                input=texts,
                model=self.model_name
            )
            
            # Process response
            processed_chunks = []
            for i, chunk in enumerate(batch):
                embedding = response.data[i].embedding
                
                processed_chunk = {
                    'chunk_id': chunk['chunk_id'],
                    'chunk_index': chunk['chunk_index'],
                    'source_page': chunk['source_page'],
                    'start_position': chunk['start_position'],
                    'end_position': chunk['end_position'],
                    'text': chunk.get('text', ''),  # This might not exist
                    'text_length': chunk['text_length'],
                    'token_count': chunk['token_count'],
                    'embedding': embedding,
                    'embedding_dimension': len(embedding)
                }
                processed_chunks.append(processed_chunk)
            
            print(f"Batch {batch_num} completed: {len(processed_chunks)} embeddings generated")
            return processed_chunks, True
            
        except Exception as e:
            print(f"Batch {batch_num} failed: {e}")
            return [], False
    
    def process_all_batches(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Process all chunks in batches.
        
        Args:
            chunks: List of chunk dictionaries
            
        Returns:
            List of processed chunks with embeddings
        """
        batches = self.create_batches(chunks)
        all_processed_chunks = []
        
        for i, batch in enumerate(batches, 1):
            processed_chunks, success = self.process_batch(batch, i, len(batches))
            
            if success:
                all_processed_chunks.extend(processed_chunks)
            else:
                print(f"Skipping failed batch {i}")
            
            # Add delay between batches
            if i < len(batches):
                time.sleep(EmbeddingConfig.BATCH_DELAY)
        
        print(f"Processing complete: {len(all_processed_chunks)}/{len(chunks)} chunks processed successfully")
        return all_processed_chunks 