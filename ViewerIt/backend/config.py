"""
ViewerIt Backend Configuration
Centralized settings for the application.
"""
import os
from pathlib import Path

# Base directories
BASE_DIR = Path(__file__).parent
UPLOADS_DIR = BASE_DIR / "uploads"
UPLOADS_DIR.mkdir(exist_ok=True)

# File handling settings
MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", 100))
MAX_FILE_SIZE = MAX_FILE_SIZE_MB * 1024 * 1024  # Convert to bytes

# Comparison settings
MAX_PREVIEW_ROWS = int(os.getenv("MAX_PREVIEW_ROWS", 1000))
MAX_DIFF_SAMPLES = int(os.getenv("MAX_DIFF_SAMPLES", 100))
COMPARISON_TIMEOUT = int(os.getenv("COMPARISON_TIMEOUT", 300))  # 5 minutes

# Chunk settings for large files
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 50000))  # Rows per chunk
LARGE_FILE_THRESHOLD = int(os.getenv("LARGE_FILE_THRESHOLD", 100000))  # Rows

# Ollama settings
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
DEFAULT_MODEL = os.getenv("DEFAULT_OLLAMA_MODEL", "llama3.2")

# CORS settings
CORS_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:3000", 
    "http://127.0.0.1:5173",
    "http://127.0.0.1:3000",
]

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Supported file formats with descriptions
SUPPORTED_FORMATS = {
    ".csv": {
        "name": "CSV",
        "description": "Comma-separated values",
        "mime_types": ["text/csv", "application/csv"],
    },
    ".tsv": {
        "name": "TSV",
        "description": "Tab-separated values",
        "mime_types": ["text/tab-separated-values"],
    },
    ".xlsx": {
        "name": "Excel",
        "description": "Microsoft Excel (2007+)",
        "mime_types": ["application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"],
    },
    ".xls": {
        "name": "Excel (Legacy)",
        "description": "Microsoft Excel (97-2003)",
        "mime_types": ["application/vnd.ms-excel"],
    },
    ".parquet": {
        "name": "Parquet",
        "description": "Apache Parquet columnar format",
        "mime_types": ["application/octet-stream"],
    },
    ".feather": {
        "name": "Feather",
        "description": "Apache Feather format",
        "mime_types": ["application/octet-stream"],
    },
    ".json": {
        "name": "JSON",
        "description": "JavaScript Object Notation",
        "mime_types": ["application/json"],
    },
    ".jsonl": {
        "name": "JSON Lines",
        "description": "Newline-delimited JSON",
        "mime_types": ["application/jsonl"],
    },
    ".dat": {
        "name": "DAT",
        "description": "Concordance/eDiscovery format",
        "mime_types": ["application/octet-stream"],
    },
    ".txt": {
        "name": "Text",
        "description": "Plain text delimited",
        "mime_types": ["text/plain"],
    },
    ".xml": {
        "name": "XML",
        "description": "Extensible Markup Language",
        "mime_types": ["application/xml", "text/xml"],
    },
    ".zip": {
        "name": "ZIP",
        "description": "ZIP archive (auto-extracts supported files)",
        "mime_types": ["application/zip"],
    },
}

