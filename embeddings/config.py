"""
Configuration settings for the embedding pipeline.
"""

class EmbeddingConfig:
    """
    Configuration class for embedding processing.
    """
    
    # Batch processing settings
    BATCH_SIZE = 75
    BATCH_DELAY = 0.1  # Delay between batches in seconds might not be needed
    
    # Output settings
    OUTPUT_JSON = True  # for logging/testing
    OUTPUT_PARQUET = True  #for acc coding
    
    # likely not needed i dont see it failing unkless its broken
    MAX_RETRIES = 0  #if later needed but unlikely might remove
    TIMEOUT = 30  # API timeout in seconds
    
    # File settings since for now we just downloading file
    EMBEDDINGS_FOLDER = "embeddings"
    
    @classmethod
    def update_batch_size(cls, new_size: int):
        """Update batch size for different use cases."""
        cls.BATCH_SIZE = new_size
        print(f"Batch size updated to: {new_size}") 