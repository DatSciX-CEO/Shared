"""
ViewerIt Backend Configuration
Centralized settings for the application.
All configurations are local-only - no external services or telemetry.
"""
import os
from pathlib import Path

# =============================================================================
# BASE DIRECTORIES
# =============================================================================
BASE_DIR = Path(__file__).parent
UPLOADS_DIR = BASE_DIR / "uploads"
UPLOADS_DIR.mkdir(exist_ok=True)

# =============================================================================
# FILE HANDLING SETTINGS
# =============================================================================
MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", 100))
MAX_FILE_SIZE = MAX_FILE_SIZE_MB * 1024 * 1024  # Convert to bytes

# Dangerous filename patterns to block (path traversal, injection)
DANGEROUS_FILENAME_PATTERNS = [
    r'\.\.', r'\\', r'/', r'\x00',  # Path traversal
    r'^\.', r'^\$', r'^~',  # Hidden/system files
    r'[<>:"|?*]',  # Invalid Windows characters
]

# Common delimiters for auto-detection
FILE_DELIMITERS = [",", "\t", "|", ";", "\x14"]

# =============================================================================
# COMPARISON SETTINGS
# =============================================================================
MAX_PREVIEW_ROWS = int(os.getenv("MAX_PREVIEW_ROWS", 1000))
MAX_DIFF_SAMPLES = int(os.getenv("MAX_DIFF_SAMPLES", 100))
COMPARISON_TIMEOUT = int(os.getenv("COMPARISON_TIMEOUT", 300))  # 5 minutes

# Chunk settings for large files
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 50000))  # Rows per chunk
LARGE_FILE_THRESHOLD = int(os.getenv("LARGE_FILE_THRESHOLD", 100000))  # Rows

# =============================================================================
# AI / OLLAMA SETTINGS (LOCAL ONLY)
# =============================================================================
# Ollama runs locally - never connects to external AI services
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
DEFAULT_MODEL = os.getenv("DEFAULT_OLLAMA_MODEL", "llama3.2")

# Preferred models in priority order for auto-selection
AI_PREFERRED_MODELS = ["llama3.2", "llama3.1", "llama3", "mistral", "phi3", "gemma2", "qwen2"]
AI_DEFAULT_MODELS = ["llama3.2", "mistral", "phi3", "gemma2"]

# AI System Prompts - centralized for easy customization
AI_SYSTEM_PROMPTS = {
    "analysis": """You are an expert data analyst specializing in eDiscovery and legal data comparison. 
You analyze data differences between datasets and provide actionable insights.
Always be precise about numbers and specific about which dataset has issues.
Format your responses with clear sections and bullet points for readability.""",
    
    "join_suggestion": """You are a data schema expert. Analyze column names and suggest the best join keys.
Focus on:
1. Primary keys or IDs
2. Document identifiers (DocID, BatesNumber, etc.)
3. Unique record identifiers
Return your answer as JSON: {"suggested_columns": ["col1"], "reasoning": "explanation"}""",
    
    "diff_explanation": """You are a data quality expert. Analyze data differences and explain:
1. Pattern of differences (consistent transformations?)
2. Potential causes (encoding, formatting, data entry errors?)
3. Which dataset has the correct/preferred format
4. Recommendations for data reconciliation""",
}

# =============================================================================
# DATA QUALITY VALIDATION PATTERNS
# =============================================================================
QUALITY_FORMAT_PATTERNS = {
    'email': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
    'phone_us': r'^\+?1?[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}$',
    'phone_intl': r'^\+?\d{1,4}[-.\s]?\d{1,14}$',
    'date_iso': r'^\d{4}-\d{2}-\d{2}$',
    'date_us': r'^\d{1,2}/\d{1,2}/\d{4}$',
    'zip_us': r'^\d{5}(-\d{4})?$',
    'url': r'^https?://[^\s]+$',
    'uuid': r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$',
    'numeric_id': r'^\d+$',
    'ssn': r'^\d{3}-\d{2}-\d{4}$',
    'ipv4': r'^(?:(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(?:25[0-5]|2[0-4]\d|[01]?\d\d?)$',
}

# =============================================================================
# CORS SETTINGS (LOCAL DEVELOPMENT)
# =============================================================================
CORS_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:3000", 
    "http://127.0.0.1:5173",
    "http://127.0.0.1:3000",
]

# =============================================================================
# LOGGING
# =============================================================================
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# =============================================================================
# RATE LIMITING
# =============================================================================
RATE_LIMIT_REQUESTS = int(os.getenv("RATE_LIMIT_REQUESTS", 100))  # requests per window
RATE_LIMIT_WINDOW = int(os.getenv("RATE_LIMIT_WINDOW", 60))  # seconds

# =============================================================================
# TASK MANAGEMENT (IN-MEMORY)
# =============================================================================
TASK_RESULT_TTL = int(os.getenv("TASK_RESULT_TTL", 3600))  # seconds to keep results
TASK_CLEANUP_INTERVAL = int(os.getenv("TASK_CLEANUP_INTERVAL", 300))  # cleanup every 5 min

# =============================================================================
# SUPPORTED FILE FORMATS
# =============================================================================
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

# Simple format map for FileHandler
SUPPORTED_FORMATS_SIMPLE = {
    ".csv": "CSV",
    ".tsv": "TSV (Tab-separated)",
    ".xlsx": "Excel",
    ".xls": "Excel (Legacy)",
    ".parquet": "Parquet",
    ".feather": "Feather",
    ".json": "JSON",
    ".jsonl": "JSON Lines",
    ".dat": "DAT (Concordance)",
    ".txt": "Text/Delimited",
    ".xml": "XML",
    ".zip": "ZIP Archive",
}

