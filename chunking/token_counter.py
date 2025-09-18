import tiktoken
from typing import List, Dict, Any

class TokenCounter:
    """
    Handles token counting using tiktoken for accurate token estimation.
    """
    
    def __init__(self, model_name: str = "text-embedding-3-large"):
        """
        Initialize token counter with specified model.
        
        Args:
            model_name: OpenAI model name for tokenizer
        """
        try:
            self.encoding = tiktoken.encoding_for_model(model_name)
        except KeyError:
            # Fallback to cl100k_base encoding if model not found
            self.encoding = tiktoken.get_encoding("cl100k_base")
    
    def count_tokens(self, text: str) -> int:
        """
        Count tokens in text.
        
        Args:
            text: Text to count tokens for
            
        Returns:
            Number of tokens
        """
        if not text:
            return 0
        return len(self.encoding.encode(text))
    
    def count_tokens_batch(self, texts: List[str]) -> List[int]:
        """
        Count tokens for multiple texts.
        
        Args:
            texts: List of texts to count tokens for
            
        Returns:
            List of token counts
        """
        return [self.count_tokens(text) for text in texts]
    
    def get_token_info(self, text: str) -> Dict[str, Any]:
        """
        Get detailed token information for text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary with token information
        """
        if not text:
            return {
                'token_count': 0,
                'character_count': 0,
                'tokens_per_character': 0
            }
        
        token_count = self.count_tokens(text)
        char_count = len(text)
        
        return {
            'token_count': token_count,
            'character_count': char_count,
            'tokens_per_character': token_count / char_count if char_count > 0 else 0
        } 