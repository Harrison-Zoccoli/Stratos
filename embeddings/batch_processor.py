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
    
    def process_batch(self, batch_metadata: List[Dict[str, Any]], batch_texts: List[str], batch_num: int, total_batches: int) -> Tuple[List[Dict[str, Any]], bool]:
        """
        Process a single batch of chunks.
        
        Args:
            batch_metadata: List of chunk metadata dictionaries
            batch_texts: List of corresponding chunk texts
            batch_num: Current batch number (1-based)
            total_batches: Total number of batches
            
        Returns:
            Tuple of (processed_chunks, success_flag)
        """
        print(f"Processing batch {batch_num}/{total_batches} ({len(batch_metadata)} chunks)...")
        
        try:
            # Use the actual chunk texts
            response = self.client.embeddings.create(
                input=batch_texts,
                model=self.model_name
            )
            
            # Process response
            processed_chunks = []
            for i, chunk_metadata in enumerate(batch_metadata):
                embedding = response.data[i].embedding
                
                processed_chunk = {
                    'chunk_id': chunk_metadata['chunk_id'],
                    'chunk_index': chunk_metadata['chunk_index'],
                    'source_page': chunk_metadata['source_page'],
                    'start_position': chunk_metadata['start_position'],
                    'end_position': chunk_metadata['end_position'],
                    'text': batch_texts[i],  # Use the actual chunk text
                    'text_length': chunk_metadata['text_length'],
                    'token_count': chunk_metadata['token_count'],
                    'embedding': embedding,
                    'embedding_dimension': len(embedding)
                }
                processed_chunks.append(processed_chunk)
            
            print(f"Batch {batch_num} completed: {len(processed_chunks)} embeddings generated")
            return processed_chunks, True
            
        except Exception as e:
            print(f"Batch {batch_num} failed: {e}")
            return [], False
    
    def process_all_batches(self, chunks_metadata: List[Dict[str, Any]], chunks_texts: List[str]) -> List[Dict[str, Any]]:
        """
        Process all chunks in batches.
        
        Args:
            chunks_metadata: List of chunk metadata dictionaries
            chunks_texts: List of corresponding chunk texts
            
        Returns:
            List of processed chunks with embeddings
        """
        # Create batches for both metadata and texts
        batches_metadata = []
        batches_texts = []
        
        for i in range(0, len(chunks_metadata), EmbeddingConfig.BATCH_SIZE):
            batch_metadata = chunks_metadata[i:i + EmbeddingConfig.BATCH_SIZE]
            batch_texts = chunks_texts[i:i + EmbeddingConfig.BATCH_SIZE]
            batches_metadata.append(batch_metadata)
            batches_texts.append(batch_texts)
        
        print(f"Created {len(batches_metadata)} batches of up to {EmbeddingConfig.BATCH_SIZE} chunks each")
        
        all_processed_chunks = []
        
        for i, (batch_metadata, batch_texts) in enumerate(zip(batches_metadata, batches_texts), 1):
            processed_chunks, success = self.process_batch(batch_metadata, batch_texts, i, len(batches_metadata))
            
            if success:
                all_processed_chunks.extend(processed_chunks)
            else:
                print(f"Skipping failed batch {i}")
            
            # Add delay between batches
            if i < len(batches_metadata):
                time.sleep(EmbeddingConfig.BATCH_DELAY)
        
        print(f"Processing complete: {len(all_processed_chunks)}/{len(chunks_metadata)} chunks processed successfully")
        return all_processed_chunks 