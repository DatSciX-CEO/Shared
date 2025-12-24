"""
ViewerIt Backend - FastAPI Application
eDiscovery Data Comparison & AI Analysis Platform
"""
from fastapi import FastAPI, File, UploadFile, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
import uvicorn

from services import FileHandler, DataComparator, AIService

app = FastAPI(
    title="ViewerIt API",
    description="eDiscovery Data Comparison & AI Analysis Backend",
    version="1.0.0",
)

# CORS Configuration for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============== Pydantic Models ==============

class CompareRequest(BaseModel):
    session_id: str
    file1: str
    file2: str
    join_columns: list[str]
    ignore_columns: Optional[list[str]] = None
    abs_tol: float = 0.0001
    rel_tol: float = 0.0

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

# ============== Health & Info ==============

@app.get("/")
async def root():
    return {
        "name": "ViewerIt API",
        "status": "online",
        "version": "1.0.0",
        "endpoints": ["/upload", "/compare", "/ai/models", "/ai/analyze"],
    }

@app.get("/health")
async def health():
    return {"status": "healthy"}

# ============== File Operations ==============

@app.post("/upload")
async def upload_files(files: list[UploadFile] = File(...)):
    """Upload one or more files for comparison."""
    if len(files) < 1:
        raise HTTPException(status_code=400, detail="At least one file required")
    
    session_id = None
    uploaded = []
    
    for file in files:
        content = await file.read()
        if session_id is None:
            session_id = FileHandler.save_uploaded_file(content, file.filename)
        else:
            # Save to same session
            from pathlib import Path
            session_dir = Path(__file__).parent / "uploads" / session_id
            file_path = session_dir / file.filename
            with open(file_path, "wb") as f:
                f.write(content)
        
        uploaded.append(file.filename)
    
    return {
        "session_id": session_id,
        "files": uploaded,
        "message": f"Successfully uploaded {len(uploaded)} file(s)",
    }

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
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/files/{session_id}/{filename}/preview")
async def preview_file(session_id: str, filename: str, rows: int = Query(default=100, le=1000)):
    """Preview the first N rows of a file."""
    try:
        df = FileHandler.load_dataframe(session_id, filename)
        preview_df = df.head(rows)
        return {
            "columns": df.columns.tolist(),
            "data": preview_df.to_dict(orient="records"),
            "total_rows": len(df),
            "preview_rows": len(preview_df),
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/files/{session_id}")
async def cleanup_session(session_id: str):
    """Delete all files for a session."""
    success = FileHandler.cleanup_session(session_id)
    if success:
        return {"message": "Session cleaned up"}
    raise HTTPException(status_code=404, detail="Session not found")

# ============== Comparison Operations ==============

@app.post("/compare")
async def compare_files(request: CompareRequest):
    """Compare two files and return detailed results."""
    try:
        df1 = FileHandler.load_dataframe(request.session_id, request.file1)
        df2 = FileHandler.load_dataframe(request.session_id, request.file2)
        
        comparator = DataComparator(df1, df2, request.file1, request.file2)
        results = comparator.compare(
            join_columns=request.join_columns,
            ignore_columns=request.ignore_columns,
            abs_tol=request.abs_tol,
            rel_tol=request.rel_tol,
        )
        
        # Add statistics
        results["statistics"] = comparator.get_statistics()
        
        return results
    except Exception as e:
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
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# ============== AI Operations ==============

@app.get("/ai/models")
async def get_ai_models():
    """Get list of available Ollama models."""
    models = AIService.get_available_models()
    return {"models": models}

@app.post("/ai/analyze")
async def ai_analyze(request: AIAnalyzeRequest):
    """Use AI to analyze comparison results."""
    result = AIService.analyze_comparison(
        model_name=request.model,
        comparison_summary=request.comparison_summary,
        user_prompt=request.prompt,
    )
    return result

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

