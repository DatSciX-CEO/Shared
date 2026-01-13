"""
Configuration for LexSpend
"""
import os

# Ollama Model Configuration
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "mistral:7b")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# GNN Model Configuration
GNN_EMBEDDING_DIM = 128
GNN_HIDDEN_DIM = 64
GNN_EPOCHS = 50
GNN_LEARNING_RATE = 0.001

# Sentence-BERT Model
SENTENCE_BERT_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
EMBEDDING_DIM = 384

# SQLite Database
DB_PATH = "lexspend_results.db"

