"""
ViewerIt Backend - FastAPI Application
eDiscovery Data Comparison & AI Analysis Platform
Enhanced with multi-file comparison, schema analysis, and quality checking.

100% LOCAL ONLY - No external services or telemetry.
"""
import time
import asyncio
import json
from collections import defaultdict
from pathlib import Path
from fastapi import FastAPI, File, UploadFile, HTTPException, Query, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, Field, field_validator
from typing import Optional
import uvicorn
import logging

from services import (
    FileHandler, 
    DataComparator, 
    AIService,
    MultiFileComparator,
    SchemaAnalyzer,
    QualityChecker,
    MultiDatasetQualityChecker,
    task_store,
    TaskStatus,
)
from services.chunked_processor import ChunkedProcessor, LARGE_FILE_THRESHOLD
from config import (
    CORS_ORIGINS, 
    SUPPORTED_FORMATS, 
    LOG_LEVEL,
    RATE_LIMIT_REQUESTS,
    RATE_LIMIT_WINDOW,
)

# Configure logging
logging.basicConfig(level=LOG_LEVEL)
logger = logging.getLogger(__name__)


class RateLimiter:
    """
    Simple in-memory rate limiter using sliding window.
    Limits requests per IP address to prevent abuse.
    100% local - no external services.
    """
    
    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: dict[str, list[float]] = defaultdict(list)
    
    def is_allowed(self, client_ip: str) -> bool:
        """Check if a request from this IP is allowed."""
        now = time.time()
        window_start = now - self.window_seconds
        
        # Clean old requests outside the window
        self.requests[client_ip] = [
            t for t in self.requests[client_ip] if t > window_start
        ]
        
        # Check if under limit
        if len(self.requests[client_ip]) < self.max_requests:
            self.requests[client_ip].append(now)
            return True
        
        return False
    
    def get_remaining(self, client_ip: str) -> int:
        """Get remaining requests for this IP in the current window."""
        now = time.time()
        window_start = now - self.window_seconds
        
        current_requests = len([
            t for t in self.requests[client_ip] if t > window_start
        ])
        
        return max(0, self.max_requests - current_requests)
    
    def get_reset_time(self, client_ip: str) -> float:
        """Get seconds until the rate limit window resets."""
        if not self.requests[client_ip]:
            return 0
        
        oldest_in_window = min(self.requests[client_ip])
        return max(0, oldest_in_window + self.window_seconds - time.time())


# Initialize rate limiter with config values
rate_limiter = RateLimiter(RATE_LIMIT_REQUESTS, RATE_LIMIT_WINDOW)

app = FastAPI(
    title="ViewerIt API",
    description="eDiscovery Data Comparison & AI Analysis Backend - Enhanced",
    version="2.0.0",
)

# CORS Configuration for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    """
    Rate limiting middleware to prevent API abuse.
    Returns 429 Too Many Requests when limit is exceeded.
    """
    # Get client IP (handle proxy headers)
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        client_ip = forwarded.split(",")[0].strip()
    else:
        client_ip = request.client.host if request.client else "unknown"
    
    # Skip rate limiting for health checks
    if request.url.path in ["/", "/health"]:
        return await call_next(request)
    
    if not rate_limiter.is_allowed(client_ip):
        reset_time = rate_limiter.get_reset_time(client_ip)
        return JSONResponse(
            status_code=429,
            content={
                "detail": "Rate limit exceeded. Please slow down.",
                "retry_after": round(reset_time, 1),
            },
            headers={
                "Retry-After": str(int(reset_time) + 1),
                "X-RateLimit-Limit": str(RATE_LIMIT_REQUESTS),
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": str(int(time.time() + reset_time)),
            },
        )
    
    # Add rate limit headers to successful responses
    response = await call_next(request)
    remaining = rate_limiter.get_remaining(client_ip)
    response.headers["X-RateLimit-Limit"] = str(RATE_LIMIT_REQUESTS)
    response.headers["X-RateLimit-Remaining"] = str(remaining)
    
    return response


# ============== Pydantic Models ==============

class CompareRequest(BaseModel):
    session_id: str
    files: list[str]
    join_columns: list[str]
    ignore_columns: Optional[list[str]] = None
    abs_tol: float = Field(default=0.0001, ge=0.0, le=1.0, description="Absolute tolerance for numeric comparison")
    rel_tol: float = Field(default=0.0, ge=0.0, le=1.0, description="Relative tolerance for numeric comparison")

    @field_validator('abs_tol', 'rel_tol')
    @classmethod
    def validate_tolerance(cls, v: float) -> float:
        if v < 0:
            raise ValueError('Tolerance must be non-negative')
        if v > 1:
            raise ValueError('Tolerance must be at most 1.0')
        return v

class MultiCompareRequest(BaseModel):
    session_id: str
    files: list[str]
    join_columns: list[str]
    ignore_columns: Optional[list[str]] = None
    use_chunked: bool = False  # Enable chunked processing for large files

class SchemaAnalysisRequest(BaseModel):
    session_id: str
    files: list[str]

class QualityCheckRequest(BaseModel):
    session_id: str
    files: list[str]

class AIAnalyzeRequest(BaseModel):
    model: str
    prompt: str
    comparison_summary: dict

class AISuggestRequest(BaseModel):
    model: str
    df1_columns: list[str]
    df2_columns: list[str]

class AIExplainRequest(BaseModel):
    model: str
    column_name: str
    differences: list[dict]

class AIStreamRequest(BaseModel):
    model: str
    prompt: str
    comparison_summary: dict


# ============== Background Task Functions ==============

def run_comparison_task(
    task_id: str,
    session_id: str,
    files: list[str],
    join_columns: list[str],
    ignore_columns: list[str] | None,
    abs_tol: float,
    rel_tol: float,
):
    """Background task for pairwise file comparison."""
    try:
        task_store.update_progress(task_id, 10, "Loading base file...")
        
        base_file = files[0]
        df_base = FileHandler.load_dataframe(session_id, base_file)
        
        comparisons = []
        total_comparisons = len(files) - 1
        
        for idx, other_file in enumerate(files[1:]):
            progress = 10 + int((idx / total_comparisons) * 80)
            task_store.update_progress(
                task_id, progress, f"Comparing {base_file} vs {other_file}..."
            )
            
            df_other = FileHandler.load_dataframe(session_id, other_file)
            
            comparator = DataComparator(df_base, df_other, base_file, other_file)
            result = comparator.compare(
                join_columns=join_columns,
                ignore_columns=ignore_columns,
                abs_tol=abs_tol,
                rel_tol=rel_tol,
            )
            
            result["statistics"] = comparator.get_statistics()
            result["file1"] = base_file
            result["file2"] = other_file
            
            comparisons.append(result)
        
        task_store.complete_task(task_id, {"comparisons": comparisons})
        
    except Exception as e:
        logger.error(f"Comparison task {task_id} failed: {str(e)}")
        task_store.fail_task(task_id, str(e))


def run_multi_comparison_task(
    task_id: str,
    session_id: str,
    files: list[str],
    join_columns: list[str],
    ignore_columns: list[str] | None,
):
    """Background task for multi-file comparison."""
    try:
        task_store.update_progress(task_id, 10, "Loading dataframes...")
        
        dataframes = {}
        for idx, filename in enumerate(files):
            progress = 10 + int((idx / len(files)) * 30)
            task_store.update_progress(task_id, progress, f"Loading {filename}...")
            df = FileHandler.load_dataframe(session_id, filename)
            dataframes[filename] = df
        
        task_store.update_progress(task_id, 50, "Performing multi-file comparison...")
        
        comparator = MultiFileComparator(dataframes)
        result = comparator.compare(
            join_columns=join_columns,
            ignore_columns=ignore_columns,
        )
        
        task_store.update_progress(task_id, 90, "Generating reconciliation report...")
        result["reconciliation_report"] = comparator.get_reconciliation_report()
        
        task_store.complete_task(task_id, result)
        
    except Exception as e:
        logger.error(f"Multi-comparison task {task_id} failed: {str(e)}")
        task_store.fail_task(task_id, str(e))


def run_quality_check_task(
    task_id: str,
    session_id: str,
    files: list[str],
):
    """Background task for quality checking."""
    try:
        if len(files) == 1:
            task_store.update_progress(task_id, 20, f"Loading {files[0]}...")
            filename = files[0]
            df = FileHandler.load_dataframe(session_id, filename)
            
            task_store.update_progress(task_id, 50, "Running quality checks...")
            checker = QualityChecker(df, filename)
            result = checker.check_all()
        else:
            dataframes = {}
            for idx, filename in enumerate(files):
                progress = 10 + int((idx / len(files)) * 40)
                task_store.update_progress(task_id, progress, f"Loading {filename}...")
                df = FileHandler.load_dataframe(session_id, filename)
                dataframes[filename] = df
            
            task_store.update_progress(task_id, 60, "Running multi-dataset quality checks...")
            checker = MultiDatasetQualityChecker(dataframes)
            result = checker.check_all()
        
        task_store.complete_task(task_id, result)
        
    except Exception as e:
        logger.error(f"Quality check task {task_id} failed: {str(e)}")
        task_store.fail_task(task_id, str(e))


# ============== Health & Info ==============

@app.get("/")
async def root():
    return {
        "name": "ViewerIt API",
        "status": "online",
        "version": "2.0.0",
        "features": [
            "Multi-file comparison (3+ files)",
            "Schema analysis",
            "Data quality checking",
            "AI-powered analysis",
            "Enhanced file format support",
        ],
        "endpoints": [
            "/upload", 
            "/compare", 
            "/compare/multi",
            "/schema/analyze",
            "/quality/check",
            "/ai/models", 
            "/ai/analyze",
        ],
    }

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.get("/formats")
async def get_supported_formats():
    """Get list of supported file formats."""
    return {"formats": SUPPORTED_FORMATS}

# ============== File Operations ==============

@app.post("/upload")
async def upload_files(files: list[UploadFile] = File(...)):
    """Upload one or more files for comparison."""
    if len(files) < 1:
        raise HTTPException(status_code=400, detail="At least one file required")
    
    session_id = None
    uploaded = []
    errors = []
    
    for file in files:
        try:
            content = await file.read()
            if session_id is None:
                session_id = FileHandler.save_uploaded_file(content, file.filename)
            else:
                FileHandler.save_uploaded_file(content, file.filename, session_id)
            
            uploaded.append(file.filename)
        except ValueError as e:
            errors.append({"file": file.filename, "error": str(e)})
        except Exception as e:
            errors.append({"file": file.filename, "error": f"Upload failed: {str(e)}"})
    
    response = {
        "session_id": session_id,
        "files": uploaded,
        "message": f"Successfully uploaded {len(uploaded)} file(s)",
    }
    
    if errors:
        response["errors"] = errors
    
    return response

@app.get("/files/{session_id}")
async def get_session_files(session_id: str):
    """Get list of files in a session."""
    files = FileHandler.get_session_files(session_id)
    if not files:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"session_id": session_id, "files": files}

@app.get("/files/{session_id}/{filename}/info")
async def get_file_info(session_id: str, filename: str):
    """Get metadata about an uploaded file."""
    try:
        info = FileHandler.get_file_info(session_id, filename)
        return info
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/files/{session_id}/{filename}/preview")
async def preview_file(session_id: str, filename: str, rows: int = Query(default=100, le=1000)):
    """Preview the first N rows of a file."""
    try:
        preview = FileHandler.preview_file(session_id, filename, rows)
        return preview
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/files/{session_id}/{filename}/sheets")
async def get_excel_sheets(session_id: str, filename: str):
    """Get list of sheets in an Excel file."""
    sheets = FileHandler.get_excel_sheets(session_id, filename)
    return {"filename": filename, "sheets": sheets}

@app.delete("/files/{session_id}")
async def cleanup_session(session_id: str):
    """Delete all files for a session."""
    success = FileHandler.cleanup_session(session_id)
    if success:
        return {"message": "Session cleaned up"}
    raise HTTPException(status_code=404, detail="Session not found")

@app.post("/formats/detect")
async def detect_format(file: UploadFile = File(...)):
    """Auto-detect file format from uploaded file."""
    content = await file.read()
    result = FileHandler.detect_format(file.filename, content)
    return result

# ============== Pairwise Comparison Operations ==============

@app.post("/compare")
async def compare_files(request: CompareRequest, background_tasks: BackgroundTasks):
    """
    Compare two or more files (pairwise) and return detailed results.
    Returns task_id for async processing - poll /tasks/{task_id} for results.
    """
    try:
        if len(request.files) < 2:
            raise HTTPException(status_code=400, detail="At least two files are required for comparison")
        
        # Validate files exist before starting task
        for filename in request.files:
            files = FileHandler.get_session_files(request.session_id)
            if filename not in files:
                raise HTTPException(status_code=404, detail=f"File not found: {filename}")
        
        # Create task and start background processing
        task = task_store.create_task("comparison")
        
        background_tasks.add_task(
            run_comparison_task,
            task.id,
            request.session_id,
            request.files,
            request.join_columns,
            request.ignore_columns,
            request.abs_tol,
            request.rel_tol,
        )
        
        return {
            "task_id": task.id,
            "status": "pending",
            "message": f"Comparison task started for {len(request.files)} files",
            "poll_url": f"/tasks/{task.id}",
        }
        
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Comparison error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/compare/sync")
async def compare_files_sync(request: CompareRequest):
    """
    Synchronous comparison (immediate result, no task polling).
    Use for small files or when immediate response is needed.
    """
    try:
        if len(request.files) < 2:
            raise HTTPException(status_code=400, detail="At least two files are required for comparison")

        base_file = request.files[0]
        df_base = FileHandler.load_dataframe(request.session_id, base_file)
        
        comparisons = []
        
        for other_file in request.files[1:]:
            df_other = FileHandler.load_dataframe(request.session_id, other_file)
            
            comparator = DataComparator(df_base, df_other, base_file, other_file)
            result = comparator.compare(
                join_columns=request.join_columns,
                ignore_columns=request.ignore_columns,
                abs_tol=request.abs_tol,
                rel_tol=request.rel_tol,
            )
            
            # Add statistics
            result["statistics"] = comparator.get_statistics()
            result["file1"] = base_file
            result["file2"] = other_file
            
            comparisons.append(result)
        
        return {"comparisons": comparisons}
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Comparison error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/compare/column-diff")
async def get_column_differences(
    session_id: str,
    file1: str,
    file2: str,
    join_columns: list[str],
    diff_column: str,
    limit: int = Query(default=100, le=1000)
):
    """Get detailed differences for a specific column."""
    try:
        df1 = FileHandler.load_dataframe(session_id, file1)
        df2 = FileHandler.load_dataframe(session_id, file2)
        
        comparator = DataComparator(df1, df2, file1, file2)
        comparator.compare(join_columns=join_columns)
        
        diffs = comparator.get_detailed_diff(diff_column, limit)
        return {"column": diff_column, "differences": diffs, "count": len(diffs)}
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# ============== Multi-File Comparison Operations ==============

# Initialize chunked processor
chunked_processor = ChunkedProcessor()


def _get_file_path(session_id: str, filename: str) -> Path:
    """Get the full path to an uploaded file."""
    from services.file_handler import UPLOADS_DIR
    return UPLOADS_DIR / session_id / filename


def _estimate_file_rows(session_id: str, filename: str) -> tuple[int, bool]:
    """Estimate row count and whether file is large."""
    file_path = _get_file_path(session_id, filename)
    if not file_path.exists():
        return 0, False
    
    is_large = chunked_processor.is_large_file(file_path)
    # Rough estimate: file_size / 100 bytes per row
    estimated_rows = file_path.stat().st_size // 100
    return estimated_rows, is_large


@app.post("/compare/multi")
async def compare_multiple_files(request: MultiCompareRequest, background_tasks: BackgroundTasks):
    """
    Compare 3+ files simultaneously with cross-file reconciliation.
    Returns task_id for async processing - poll /tasks/{task_id} for results.
    
    For large files, set use_chunked=True for memory-efficient processing.
    """
    try:
        if len(request.files) < 2:
            raise HTTPException(status_code=400, detail="At least 2 files required")
        
        # Validate files exist before starting task
        for filename in request.files:
            files = FileHandler.get_session_files(request.session_id)
            if filename not in files:
                raise HTTPException(status_code=404, detail=f"File not found: {filename}")
        
        # Check if any files are large
        large_files = []
        for filename in request.files:
            _, is_large = _estimate_file_rows(request.session_id, filename)
            if is_large:
                large_files.append(filename)
        
        warnings = []
        if large_files and not request.use_chunked:
            warnings.append({
                "type": "large_files_detected",
                "files": large_files,
                "message": f"{len(large_files)} large file(s) detected.",
                "suggestion": "Set use_chunked=True for memory-efficient processing."
            })
        
        # Create task and start background processing
        task = task_store.create_task("multi_comparison")
        
        background_tasks.add_task(
            run_multi_comparison_task,
            task.id,
            request.session_id,
            request.files,
            request.join_columns,
            request.ignore_columns,
        )
        
        response = {
            "task_id": task.id,
            "status": "pending",
            "message": f"Multi-file comparison started for {len(request.files)} files",
            "poll_url": f"/tasks/{task.id}",
        }
        
        if warnings:
            response["warnings"] = warnings
        
        return response
        
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Multi-comparison error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/compare/multi/sync")
async def compare_multiple_files_sync(request: MultiCompareRequest):
    """
    Synchronous multi-file comparison (immediate result, no task polling).
    Use for small files or when immediate response is needed.
    """
    try:
        if len(request.files) < 2:
            raise HTTPException(status_code=400, detail="At least 2 files required")
        
        # Check if any files are large
        large_files = []
        for filename in request.files:
            _, is_large = _estimate_file_rows(request.session_id, filename)
            if is_large:
                large_files.append(filename)
        
        # Warn about large files if not using chunked processing
        warnings = []
        if large_files and not request.use_chunked:
            warnings.append({
                "type": "large_files_detected",
                "files": large_files,
                "message": f"{len(large_files)} large file(s) detected. Consider using use_chunked=True for better performance.",
                "suggestion": "Set use_chunked=True in the request for memory-efficient processing."
            })
        
        # Load all dataframes
        dataframes = {}
        for filename in request.files:
            df = FileHandler.load_dataframe(request.session_id, filename)
            dataframes[filename] = df
        
        # Perform multi-file comparison
        comparator = MultiFileComparator(dataframes)
        result = comparator.compare(
            join_columns=request.join_columns,
            ignore_columns=request.ignore_columns,
        )
        
        # Add reconciliation report
        result["reconciliation_report"] = comparator.get_reconciliation_report()
        
        # Add warnings if any
        if warnings:
            result["warnings"] = warnings
        
        return result
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Multi-comparison error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/compare/chunked")
async def compare_large_files_chunked(
    session_id: str,
    file1: str,
    file2: str,
    join_columns: list[str]
):
    """
    Compare two large files using chunked processing.
    More memory-efficient for files with 100K+ rows.
    Returns key-based comparison without loading full files into memory.
    """
    try:
        file1_path = _get_file_path(session_id, file1)
        file2_path = _get_file_path(session_id, file2)
        
        if not file1_path.exists():
            raise HTTPException(status_code=404, detail=f"File not found: {file1}")
        if not file2_path.exists():
            raise HTTPException(status_code=404, detail=f"File not found: {file2}")
        
        # Check if files are CSV (chunked processing only supports CSV currently)
        for path in [file1_path, file2_path]:
            if path.suffix.lower() != '.csv':
                raise HTTPException(
                    status_code=400, 
                    detail=f"Chunked comparison only supports CSV files. {path.name} is not CSV."
                )
        
        result = chunked_processor.compare_large_files_chunked(
            file1_path, file2_path, join_columns
        )
        
        result["file1"] = file1
        result["file2"] = file2
        result["method"] = "chunked"
        result["memory_efficient"] = True
        
        return result
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Chunked comparison error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/files/{session_id}/{filename}/chunked-stats")
async def get_chunked_file_stats(session_id: str, filename: str):
    """
    Get statistics for a large file using chunked processing.
    Memory-efficient alternative to loading the entire file.
    """
    try:
        file_path = _get_file_path(session_id, filename)
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail=f"File not found: {filename}")
        
        if file_path.suffix.lower() != '.csv':
            raise HTTPException(
                status_code=400,
                detail="Chunked statistics only available for CSV files"
            )
        
        stats = chunked_processor.get_chunked_statistics(file_path)
        stats["filename"] = filename
        stats["method"] = "chunked"
        
        return stats
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# ============== Schema Analysis Operations ==============

@app.post("/schema/analyze")
async def analyze_schemas(request: SchemaAnalysisRequest):
    """
    Perform deep schema analysis across multiple files.
    Detects column alignment, type compatibility, and suggests mappings.
    """
    try:
        if len(request.files) < 1:
            raise HTTPException(status_code=400, detail="At least 1 file required")
        
        # Load all dataframes
        dataframes = {}
        for filename in request.files:
            df = FileHandler.load_dataframe(request.session_id, filename)
            dataframes[filename] = df
        
        # Analyze schemas
        analyzer = SchemaAnalyzer(dataframes)
        result = analyzer.analyze()
        
        return result
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Schema analysis error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

# ============== Data Quality Operations ==============

@app.post("/quality/check")
async def check_data_quality(request: QualityCheckRequest, background_tasks: BackgroundTasks):
    """
    Run comprehensive data quality checks on files.
    Returns task_id for async processing - poll /tasks/{task_id} for results.
    """
    try:
        if len(request.files) < 1:
            raise HTTPException(status_code=400, detail="At least 1 file required")
        
        # Validate files exist before starting task
        for filename in request.files:
            files = FileHandler.get_session_files(request.session_id)
            if filename not in files:
                raise HTTPException(status_code=404, detail=f"File not found: {filename}")
        
        # Create task and start background processing
        task = task_store.create_task("quality_check")
        
        background_tasks.add_task(
            run_quality_check_task,
            task.id,
            request.session_id,
            request.files,
        )
        
        return {
            "task_id": task.id,
            "status": "pending",
            "message": f"Quality check started for {len(request.files)} file(s)",
            "poll_url": f"/tasks/{task.id}",
        }
        
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Quality check error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/quality/check/sync")
async def check_data_quality_sync(request: QualityCheckRequest):
    """
    Synchronous quality check (immediate result, no task polling).
    Use for small files or when immediate response is needed.
    """
    try:
        if len(request.files) < 1:
            raise HTTPException(status_code=400, detail="At least 1 file required")
        
        if len(request.files) == 1:
            # Single file quality check
            filename = request.files[0]
            df = FileHandler.load_dataframe(request.session_id, filename)
            checker = QualityChecker(df, filename)
            result = checker.check_all()
        else:
            # Multi-dataset quality comparison
            dataframes = {}
            for filename in request.files:
                df = FileHandler.load_dataframe(request.session_id, filename)
                dataframes[filename] = df
            
            checker = MultiDatasetQualityChecker(dataframes)
            result = checker.check_all()
        
        return result
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Quality check error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/quality/{session_id}/{filename}")
async def get_single_file_quality(session_id: str, filename: str):
    """Get quality metrics for a single file."""
    try:
        df = FileHandler.load_dataframe(session_id, filename)
        checker = QualityChecker(df, filename)
        result = checker.check_all()
        return result
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============== Task Management Operations ==============

@app.get("/tasks/{task_id}")
async def get_task_status(task_id: str):
    """
    Get the status and result of a background task.
    Poll this endpoint to track progress of async operations.
    """
    task = task_store.get_task(task_id)
    
    if not task:
        raise HTTPException(status_code=404, detail=f"Task not found: {task_id}")
    
    response = task.to_dict()
    
    # Include result if task is completed
    if task.status == TaskStatus.COMPLETED and task.result is not None:
        response["result"] = task.result
    
    return response


@app.get("/tasks/{task_id}/result")
async def get_task_result(task_id: str):
    """
    Get only the result of a completed task.
    Returns 202 if task is still processing.
    """
    task = task_store.get_task(task_id)
    
    if not task:
        raise HTTPException(status_code=404, detail=f"Task not found: {task_id}")
    
    if task.status == TaskStatus.FAILED:
        raise HTTPException(status_code=500, detail=task.error or "Task failed")
    
    if task.status != TaskStatus.COMPLETED:
        return JSONResponse(
            status_code=202,
            content={
                "status": task.status.value,
                "progress": task.progress,
                "message": task.message,
            }
        )
    
    return task.result


@app.get("/tasks")
async def list_tasks(limit: int = Query(default=50, le=100)):
    """List recent tasks with their status."""
    return {
        "tasks": task_store.list_tasks(limit),
        "active_count": task_store.get_active_task_count(),
    }


# ============== AI Operations ==============

@app.get("/ai/models")
async def get_ai_models():
    """Get list of available Ollama models with detailed metadata."""
    result = AIService.get_available_models()
    return result

@app.get("/ai/status")
async def get_ai_status():
    """Check Ollama service status."""
    return AIService.check_ollama_status()

@app.post("/ai/analyze")
async def ai_analyze(request: AIAnalyzeRequest):
    """Use AI to analyze comparison results (non-streaming)."""
    result = AIService.analyze_comparison(
        model_name=request.model,
        comparison_summary=request.comparison_summary,
        user_prompt=request.prompt,
    )
    return result


@app.post("/ai/analyze/stream")
async def ai_analyze_stream(request: AIStreamRequest):
    """
    Stream AI analysis via Server-Sent Events (SSE).
    Tokens are streamed as they're generated by local Ollama.
    
    Frontend should use EventSource or fetch with streaming body.
    """
    async def generate_sse():
        """Generate SSE events from Ollama stream."""
        try:
            # Send initial event
            yield f"data: {json.dumps({'type': 'start', 'model': request.model})}\n\n"
            
            # Stream tokens
            for token in AIService.analyze_comparison_stream(
                model_name=request.model,
                comparison_summary=request.comparison_summary,
                user_prompt=request.prompt,
            ):
                # Escape newlines for SSE format
                escaped_token = token.replace('\n', '\\n')
                yield f"data: {json.dumps({'type': 'token', 'content': token})}\n\n"
                # Small delay to prevent overwhelming the client
                await asyncio.sleep(0.01)
            
            # Send completion event
            yield f"data: {json.dumps({'type': 'done'})}\n\n"
            
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
    
    return StreamingResponse(
        generate_sse(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
        }
    )

@app.post("/ai/suggest-join")
async def ai_suggest_join(request: AISuggestRequest):
    """Use AI to suggest join columns for comparison."""
    result = AIService.suggest_join_columns(
        model_name=request.model,
        df1_columns=request.df1_columns,
        df2_columns=request.df2_columns,
    )
    return result

@app.post("/ai/explain-diff")
async def ai_explain_diff(request: AIExplainRequest):
    """Use AI to explain differences in a column."""
    result = AIService.explain_differences(
        model_name=request.model,
        column_name=request.column_name,
        differences=request.differences,
    )
    return result

# ============== Run Server ==============

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
