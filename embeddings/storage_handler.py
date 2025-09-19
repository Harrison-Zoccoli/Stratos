import json
import pandas as pd
from pathlib import Path
from typing import List, Dict, Any
from .config import EmbeddingConfig

class StorageHandler:
    """
    Handles saving embeddings to files in multiple formats. Later can save to vector db
    """
    
    def __init__(self):
        self.embeddings_folder = Path(EmbeddingConfig.EMBEDDINGS_FOLDER)
        if EmbeddingConfig.SAVE_EMBEDDINGS:
            self.embeddings_folder.mkdir(exist_ok=True)
    
    def save_embeddings(self, processed_chunks: List[Dict[str, Any]], pdf_name: str, summary: Dict[str, Any]) -> Dict[str, str]:
        """
        Save embeddings in both JSON and Parquet formats.
        
        Args:
            processed_chunks: List of processed chunks with embeddings
            pdf_name: Name of the source PDF
            summary: Processing summary
            
        Returns:
            Dictionary with file paths for saved files
        """
        saved_files = {}
        
        # Check if saving is enabled
        if not EmbeddingConfig.SAVE_EMBEDDINGS:
            print("Embedding file saving is disabled - skipping file output")
            return saved_files
        
        # Prepare data for saving
        embeddings_data = {
            'summary': summary,
            'chunks': processed_chunks
        }
        
        # Save JSON format
        if EmbeddingConfig.OUTPUT_JSON:
            json_file = self.embeddings_folder / f"{pdf_name}_embeddings.json"
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(embeddings_data, f, indent=2)
            saved_files['json'] = str(json_file)
            print(f"Saved JSON embeddings: {json_file}")
        
        # Save Parquet format
        if EmbeddingConfig.OUTPUT_PARQUET:
            parquet_file = self.embeddings_folder / f"{pdf_name}_embeddings.parquet"
            
            # Convert to DataFrame for Parquet
            df_data = []
            for chunk in processed_chunks:
                row = {
                    'chunk_id': chunk['chunk_id'],
                    'chunk_index': chunk['chunk_index'],
                    'source_page': chunk['source_page'],
                    'start_position': chunk['start_position'],
                    'end_position': chunk['end_position'],
                    'text': chunk['text'],
                    'text_length': chunk['text_length'],
                    'token_count': chunk['token_count'],
                    'embedding_dimension': chunk['embedding_dimension'],
                    'embedding': chunk['embedding']  # This will be stored as a list
                }
                df_data.append(row)
            
            df = pd.DataFrame(df_data)
            df.to_parquet(parquet_file, index=False)
            saved_files['parquet'] = str(parquet_file)
            print(f"Saved Parquet embeddings: {parquet_file}")
        
        return saved_files
    
    def get_embeddings_summary(self, processed_chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate summary statistics for embeddings.
        
        Args:
            processed_chunks: List of processed chunks
            
        Returns:
            Summary dictionary
        """
        if not processed_chunks:
            return {}
        
        total_chunks = len(processed_chunks)
        total_tokens = sum(chunk['token_count'] for chunk in processed_chunks)
        embedding_dimension = processed_chunks[0]['embedding_dimension']
        
        return {
            'total_chunks': total_chunks,
            'total_tokens': total_tokens,
            'embedding_dimension': embedding_dimension,
            'average_tokens_per_chunk': total_tokens / total_chunks,
            'total_embedding_size': total_chunks * embedding_dimension
        } 