"""
File Handler Service - Handles file uploads and format detection for eDiscovery data.
Supports multiple file formats with automatic detection and encoding handling.
"""
import os
import re
import uuid
import shutil
import zipfile
import io
from pathlib import Path
from typing import Optional, Union
import pandas as pd
import chardet
import logging

# Import centralized config
from config import (
    UPLOADS_DIR, 
    MAX_FILE_SIZE, 
    DANGEROUS_FILENAME_PATTERNS,
    FILE_DELIMITERS,
    SUPPORTED_FORMATS_SIMPLE,
)

logger = logging.getLogger(__name__)

# Ensure uploads directory exists
UPLOADS_DIR.mkdir(exist_ok=True)

# Use centralized patterns from config
DANGEROUS_PATTERNS = DANGEROUS_FILENAME_PATTERNS


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to prevent path traversal and injection attacks.
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename safe for filesystem operations
        
    Raises:
        ValueError: If filename is invalid or potentially dangerous
    """
    if not filename:
        raise ValueError("Filename cannot be empty")
    
    # Get just the basename (ignore any directory components)
    filename = os.path.basename(filename)
    
    # Check for dangerous patterns
    for pattern in DANGEROUS_PATTERNS:
        if re.search(pattern, filename):
            raise ValueError(f"Invalid filename: contains dangerous pattern")
    
    # Remove any non-printable characters
    filename = ''.join(c for c in filename if c.isprintable())
    
    # Ensure there's still a valid filename
    if not filename or filename.isspace():
        raise ValueError("Filename is empty after sanitization")
    
    # Limit filename length (255 is common filesystem limit)
    if len(filename) > 255:
        # Preserve extension
        name, ext = os.path.splitext(filename)
        max_name_len = 255 - len(ext)
        filename = name[:max_name_len] + ext
    
    return filename


class FileHandler:
    """Handles file operations for data comparison."""
    
    # Use centralized format definitions from config
    SUPPORTED_FORMATS = SUPPORTED_FORMATS_SIMPLE
    
    # Use centralized delimiters from config
    DELIMITERS = FILE_DELIMITERS
    
    @classmethod
    def save_uploaded_file(cls, file_content: bytes, filename: str, 
                          session_id: Optional[str] = None) -> str:
        """
        Save uploaded file and return the session ID.
        
        Args:
            file_content: Raw file bytes
            filename: Original filename
            session_id: Optional existing session ID to add file to
            
        Returns:
            Session ID
            
        Raises:
            ValueError: If file is too large, invalid, or has dangerous filename
        """
        # Sanitize filename to prevent path traversal attacks
        safe_filename = sanitize_filename(filename)
        
        # Validate file size
        if len(file_content) > MAX_FILE_SIZE:
            raise ValueError(f"File too large. Maximum size is {MAX_FILE_SIZE / (1024*1024):.0f}MB")
        
        # Create or use existing session
        if session_id is None:
            session_id = str(uuid.uuid4())
        
        # Validate session_id format (must be UUID)
        try:
            uuid.UUID(session_id, version=4)
        except ValueError:
            raise ValueError("Invalid session ID format")
        
        session_dir = UPLOADS_DIR / session_id
        session_dir.mkdir(exist_ok=True)
        
        file_path = session_dir / safe_filename
        
        # Handle ZIP files - extract contents
        ext = Path(safe_filename).suffix.lower()
        if ext == ".zip":
            return cls._handle_zip_upload(file_content, session_id, session_dir)
        
        with open(file_path, "wb") as f:
            f.write(file_content)
        
        return session_id
    
    @classmethod
    def _handle_zip_upload(cls, file_content: bytes, session_id: str, 
                          session_dir: Path) -> str:
        """Extract ZIP file and save contents with security validation."""
        try:
            with zipfile.ZipFile(io.BytesIO(file_content)) as zf:
                for zip_info in zf.infolist():
                    if zip_info.is_dir():
                        continue
                    
                    # Get just the filename (ignore directory structure)
                    raw_name = Path(zip_info.filename).name
                    
                    # Sanitize the extracted filename
                    try:
                        safe_name = sanitize_filename(raw_name)
                    except ValueError as e:
                        logger.warning(f"Skipping unsafe file in ZIP: {raw_name} - {e}")
                        continue
                    
                    # Only extract supported file types
                    ext = Path(safe_name).suffix.lower()
                    if ext in cls.SUPPORTED_FORMATS and ext != ".zip":
                        content = zf.read(zip_info.filename)
                        
                        # Validate extracted file size
                        if len(content) > MAX_FILE_SIZE:
                            logger.warning(f"Skipping oversized file in ZIP: {safe_name}")
                            continue
                        
                        file_path = session_dir / safe_name
                        with open(file_path, "wb") as f:
                            f.write(content)
                        logger.info(f"Extracted {safe_name} from ZIP")
        except zipfile.BadZipFile:
            raise ValueError("Invalid ZIP file")
        
        return session_id
    
    @classmethod
    def detect_encoding(cls, file_path: Path, sample_size: int = 10000) -> str:
        """
        Detect file encoding using chardet.
        
        Args:
            file_path: Path to file
            sample_size: Bytes to sample for detection
            
        Returns:
            Detected encoding string
        """
        with open(file_path, "rb") as f:
            raw_data = f.read(sample_size)
        
        result = chardet.detect(raw_data)
        encoding = result.get("encoding", "utf-8")
        confidence = result.get("confidence", 0)
        
        # Fall back to utf-8 if confidence is low
        if confidence < 0.7:
            encoding = "utf-8"
        
        return encoding or "utf-8"
    
    @classmethod
    def detect_delimiter(cls, file_path: Path, encoding: str = "utf-8") -> str:
        """
        Auto-detect the delimiter used in a text file.
        
        Args:
            file_path: Path to file
            encoding: File encoding
            
        Returns:
            Detected delimiter character
        """
        try:
            with open(file_path, "r", encoding=encoding, errors="replace") as f:
                # Read first few lines
                sample_lines = [f.readline() for _ in range(5)]
        except Exception:
            return ","
        
        sample_text = "".join(sample_lines)
        
        # Count occurrences of each delimiter
        delimiter_counts = {d: sample_text.count(d) for d in cls.DELIMITERS}
        
        # Return delimiter with highest count (if reasonable)
        best_delimiter = max(delimiter_counts, key=delimiter_counts.get)
        
        if delimiter_counts[best_delimiter] > 0:
            return best_delimiter
        
        return ","  # Default
    
    @classmethod
    def load_dataframe(cls, session_id: str, filename: str, 
                      sheet_name: Optional[Union[str, int]] = 0,
                      encoding: Optional[str] = None) -> pd.DataFrame:
        """
        Load a file as a pandas DataFrame.
        
        Args:
            session_id: Session ID
            filename: Filename to load
            sheet_name: For Excel files, which sheet to load
            encoding: Force specific encoding (auto-detected if None)
            
        Returns:
            Loaded DataFrame
            
        Raises:
            ValueError: If format is unsupported
            FileNotFoundError: If file doesn't exist
        """
        file_path = UPLOADS_DIR / session_id / filename
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {filename}")
        
        ext = Path(filename).suffix.lower()
        
        try:
            if ext == ".csv":
                return cls._load_csv(file_path, encoding)
            elif ext == ".tsv":
                return cls._load_csv(file_path, encoding, delimiter="\t")
            elif ext in (".xlsx", ".xls"):
                return cls._load_excel(file_path, sheet_name)
            elif ext == ".parquet":
                return pd.read_parquet(file_path)
            elif ext == ".feather":
                return pd.read_feather(file_path)
            elif ext == ".json":
                return cls._load_json(file_path)
            elif ext == ".jsonl":
                return pd.read_json(file_path, lines=True)
            elif ext in (".dat", ".txt"):
                return cls._load_delimited(file_path, encoding)
            elif ext == ".xml":
                return cls._load_xml(file_path)
            else:
                raise ValueError(f"Unsupported file format: {ext}")
        except Exception as e:
            logger.error(f"Error loading {filename}: {str(e)}")
            raise ValueError(f"Error loading file: {str(e)}")
    
    @classmethod
    def _load_csv(cls, file_path: Path, encoding: Optional[str] = None,
                  delimiter: str = ",") -> pd.DataFrame:
        """Load CSV file with encoding detection."""
        if encoding is None:
            encoding = cls.detect_encoding(file_path)
        
        try:
            return pd.read_csv(
                file_path, 
                encoding=encoding, 
                delimiter=delimiter,
                low_memory=False,
                on_bad_lines='warn'
            )
        except UnicodeDecodeError:
            # Try with latin-1 as fallback
            return pd.read_csv(
                file_path, 
                encoding="latin-1", 
                delimiter=delimiter,
                low_memory=False,
                on_bad_lines='warn'
            )
    
    @classmethod
    def _load_excel(cls, file_path: Path, 
                   sheet_name: Optional[Union[str, int]] = 0) -> pd.DataFrame:
        """Load Excel file, optionally specific sheet."""
        # If sheet_name is None, load all sheets and concatenate
        if sheet_name is None:
            excel_file = pd.ExcelFile(file_path)
            dfs = []
            for sheet in excel_file.sheet_names:
                df = pd.read_excel(excel_file, sheet_name=sheet)
                df['_sheet_name'] = sheet
                dfs.append(df)
            return pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()
        
        return pd.read_excel(file_path, sheet_name=sheet_name)
    
    @classmethod
    def _load_json(cls, file_path: Path) -> pd.DataFrame:
        """Load JSON file, handling nested structures."""
        try:
            # Try standard read
            return pd.read_json(file_path)
        except ValueError:
            # Try with normalization for nested JSON
            import json
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if isinstance(data, list):
                return pd.json_normalize(data)
            elif isinstance(data, dict):
                # Check if it's a records-style dict
                if all(isinstance(v, list) for v in data.values()):
                    return pd.DataFrame(data)
                return pd.json_normalize([data])
            
            raise ValueError("Unable to parse JSON structure")
    
    @classmethod
    def _load_delimited(cls, file_path: Path, 
                       encoding: Optional[str] = None) -> pd.DataFrame:
        """Load delimited text file with auto-detection."""
        if encoding is None:
            encoding = cls.detect_encoding(file_path)
        
        delimiter = cls.detect_delimiter(file_path, encoding)
        
        try:
            return pd.read_csv(
                file_path, 
                delimiter=delimiter, 
                encoding=encoding,
                low_memory=False,
                on_bad_lines='warn'
            )
        except UnicodeDecodeError:
            return pd.read_csv(
                file_path, 
                delimiter=delimiter, 
                encoding="latin-1",
                low_memory=False,
                on_bad_lines='warn'
            )
    
    @classmethod
    def _load_xml(cls, file_path: Path) -> pd.DataFrame:
        """Load XML file as DataFrame."""
        try:
            return pd.read_xml(file_path)
        except Exception as e:
            # Try with different parsers
            try:
                return pd.read_xml(file_path, parser='etree')
            except Exception as parse_error:
                logger.warning(f"XML parsing with etree also failed: {parse_error}")
                raise ValueError(f"Unable to parse XML: {str(e)}")
    
    @classmethod
    def get_file_info(cls, session_id: str, filename: str) -> dict:
        """
        Get detailed metadata about an uploaded file.
        
        Args:
            session_id: Session ID
            filename: Filename
            
        Returns:
            Dictionary with file metadata
        """
        file_path = UPLOADS_DIR / session_id / filename
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {filename}")
        
        file_size = file_path.stat().st_size
        ext = Path(filename).suffix.lower()
        
        # Get basic info without fully loading for large files
        info = {
            "filename": filename,
            "session_id": session_id,
            "file_size": file_size,
            "file_size_mb": round(file_size / (1024 * 1024), 2),
            "format": cls.SUPPORTED_FORMATS.get(ext, "Unknown"),
            "extension": ext,
        }
        
        # Load dataframe for detailed info
        try:
            df = cls.load_dataframe(session_id, filename)
            info.update({
                "rows": len(df),
                "columns": len(df.columns),
                "column_names": df.columns.tolist(),
                "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
                "memory_usage_mb": round(df.memory_usage(deep=True).sum() / (1024 * 1024), 2),
                "null_counts": df.isnull().sum().to_dict(),
            })
        except Exception as e:
            info["error"] = str(e)
        
        return info
    
    @classmethod
    def get_excel_sheets(cls, session_id: str, filename: str) -> list[str]:
        """Get list of sheet names from an Excel file."""
        file_path = UPLOADS_DIR / session_id / filename
        ext = Path(filename).suffix.lower()
        
        if ext not in (".xlsx", ".xls"):
            return []
        
        try:
            excel_file = pd.ExcelFile(file_path)
            return excel_file.sheet_names
        except Exception:
            return []
    
    @classmethod
    def cleanup_session(cls, session_id: str) -> bool:
        """Remove all files for a session."""
        session_dir = UPLOADS_DIR / session_id
        if session_dir.exists():
            shutil.rmtree(session_dir)
            return True
        return False
    
    @classmethod
    def get_session_files(cls, session_id: str) -> list[str]:
        """List all files in a session."""
        session_dir = UPLOADS_DIR / session_id
        if session_dir.exists():
            return [f.name for f in session_dir.iterdir() if f.is_file()]
        return []
    
    @classmethod
    def detect_format(cls, filename: str, content: Optional[bytes] = None) -> dict:
        """
        Detect file format from filename and optionally content.
        
        Args:
            filename: Filename
            content: Optional file content for deeper analysis
            
        Returns:
            Format detection results
        """
        ext = Path(filename).suffix.lower()
        
        result = {
            "extension": ext,
            "format": cls.SUPPORTED_FORMATS.get(ext, "Unknown"),
            "is_supported": ext in cls.SUPPORTED_FORMATS,
        }
        
        if content:
            # Try to detect encoding
            detected = chardet.detect(content[:10000])
            result["detected_encoding"] = detected.get("encoding")
            result["encoding_confidence"] = detected.get("confidence")
            
            # Check if it might be a different format
            if content.startswith(b'PK'):
                result["might_be"] = "ZIP or Excel (xlsx)"
            elif content.startswith(b'<?xml'):
                result["might_be"] = "XML"
            elif content.startswith(b'{') or content.startswith(b'['):
                result["might_be"] = "JSON"
        
        return result
    
    @classmethod
    def preview_file(cls, session_id: str, filename: str, 
                    rows: int = 100) -> dict:
        """
        Get a preview of file contents.
        
        Args:
            session_id: Session ID
            filename: Filename
            rows: Number of rows to preview
            
        Returns:
            Preview data
        """
        df = cls.load_dataframe(session_id, filename)
        preview_df = df.head(rows)
        
        return {
            "columns": df.columns.tolist(),
            "data": preview_df.to_dict(orient="records"),
            "total_rows": len(df),
            "preview_rows": len(preview_df),
            "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
        }
