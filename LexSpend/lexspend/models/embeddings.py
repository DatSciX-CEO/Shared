"""
Text embeddings using Sentence-BERT for line item descriptions
"""
import logging
from typing import List, Optional
import numpy as np
import pandas as pd
from transformers import AutoTokenizer, AutoModel
import torch

logger = logging.getLogger(__name__)

# Import config
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from config import SENTENCE_BERT_MODEL, EMBEDDING_DIM


class TextEmbedder:
    """Handles text embeddings using Sentence-BERT models."""
    
    def __init__(self, model_name: str = SENTENCE_BERT_MODEL):
        """
        Initialize the text embedder.
        
        Args:
            model_name: Name of the Sentence-BERT model to use
        """
        self.model_name = model_name
        self.tokenizer = None
        self.model = None
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        logger.info(f"Initializing TextEmbedder with model: {model_name} on device: {self.device}")
    
    def _load_model(self):
        """Lazy load the model and tokenizer."""
        if self.tokenizer is None or self.model is None:
            try:
                logger.info(f"Loading Sentence-BERT model: {self.model_name}")
                self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
                self.model = AutoModel.from_pretrained(self.model_name)
                self.model.to(self.device)
                self.model.eval()
                logger.info("Model loaded successfully")
            except Exception as e:
                logger.error(f"Error loading model: {e}")
                raise
    
    def embed_text(self, text: str) -> np.ndarray:
        """
        Generate embedding for a single text string.
        
        Args:
            text: Input text to embed
            
        Returns:
            NumPy array of embeddings (shape: [embedding_dim])
        """
        self._load_model()
        
        # Handle empty or None text
        if not text or pd.isna(text) or text.strip() == "":
            text = "[No Description]"
        
        try:
            # Tokenize and encode
            inputs = self.tokenizer(text, return_tensors="pt", truncation=True, max_length=512, padding=True)
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # Generate embeddings
            with torch.no_grad():
                outputs = self.model(**inputs)
                # Use mean pooling of token embeddings
                embeddings = outputs.last_hidden_state.mean(dim=1).squeeze().cpu().numpy()
            
            return embeddings
            
        except Exception as e:
            logger.error(f"Error embedding text '{text[:50]}...': {e}")
            # Return zero vector as fallback
            return np.zeros(EMBEDDING_DIM)
    
    def embed_batch(self, texts: List[str], batch_size: int = 32) -> np.ndarray:
        """
        Generate embeddings for a batch of texts.
        
        Args:
            texts: List of text strings to embed
            batch_size: Batch size for processing
            
        Returns:
            NumPy array of embeddings (shape: [num_texts, embedding_dim])
        """
        self._load_model()
        
        # Handle empty texts
        processed_texts = []
        for text in texts:
            if not text or pd.isna(text) or (isinstance(text, str) and text.strip() == ""):
                processed_texts.append("[No Description]")
            else:
                processed_texts.append(str(text))
        
        all_embeddings = []
        
        try:
            for i in range(0, len(processed_texts), batch_size):
                batch_texts = processed_texts[i:i + batch_size]
                
                # Tokenize batch
                inputs = self.tokenizer(
                    batch_texts,
                    return_tensors="pt",
                    truncation=True,
                    max_length=512,
                    padding=True
                )
                inputs = {k: v.to(self.device) for k, v in inputs.items()}
                
                # Generate embeddings
                with torch.no_grad():
                    outputs = self.model(**inputs)
                    # Mean pooling
                    batch_embeddings = outputs.last_hidden_state.mean(dim=1).cpu().numpy()
                
                all_embeddings.append(batch_embeddings)
            
            # Concatenate all batches
            embeddings = np.vstack(all_embeddings)
            return embeddings
            
        except Exception as e:
            logger.error(f"Error embedding batch: {e}")
            # Return zero vectors as fallback
            return np.zeros((len(texts), EMBEDDING_DIM))


# Global embedder instance (lazy loaded)
_embedder: Optional[TextEmbedder] = None


def get_embedder() -> TextEmbedder:
    """Get or create the global embedder instance."""
    global _embedder
    if _embedder is None:
        _embedder = TextEmbedder()
    return _embedder


# Fix import for pandas
import pandas as pd

