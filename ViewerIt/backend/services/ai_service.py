"""
AI Service - Ollama integration for intelligent data analysis.
Enhanced with detailed model metadata and intelligent auto-selection.
All AI operations are LOCAL ONLY via Ollama - no external API calls.
"""
import ollama
from typing import Optional, Generator
import json

# Import centralized config
from config import (
    AI_PREFERRED_MODELS,
    AI_DEFAULT_MODELS,
    AI_SYSTEM_PROMPTS,
    OLLAMA_BASE_URL,
)


class AIService:
    """Handles AI-powered analysis using local Ollama models only."""
    
    # Use centralized model preferences from config
    PREFERRED_MODELS = AI_PREFERRED_MODELS
    DEFAULT_MODELS = AI_DEFAULT_MODELS
    
    @classmethod
    def _format_size(cls, size_bytes: int) -> str:
        """Convert bytes to human-readable size string."""
        if size_bytes == 0:
            return "Unknown"
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if abs(size_bytes) < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} PB"
    
    @classmethod
    def _extract_quantization(cls, model_name: str, details: dict) -> str:
        """Extract quantization level from model name or details."""
        # Common quantization patterns
        quant_patterns = ['q4_0', 'q4_1', 'q4_k_m', 'q4_k_s', 'q5_0', 'q5_1', 
                         'q5_k_m', 'q5_k_s', 'q6_k', 'q8_0', 'fp16', 'f16', 'f32']
        
        name_lower = model_name.lower()
        for pattern in quant_patterns:
            if pattern in name_lower:
                return pattern.upper()
        
        # Check details for quantization info
        quant = details.get("quantization_level", "")
        if quant:
            return quant.upper()
        
        return "Default"
    
    @classmethod
    def _extract_parameter_count(cls, details: dict) -> str:
        """Extract parameter count from model details."""
        param_size = details.get("parameter_size", "")
        if param_size:
            return param_size
        
        # Try to infer from family/format
        families = details.get("families", [])
        if families:
            return ", ".join(families)
        
        return "Unknown"
    
    @classmethod
    def check_ollama_status(cls) -> dict:
        """Check if Ollama is running and accessible."""
        try:
            response = ollama.list()
            model_count = len(response.get("models", []))
            return {
                "online": True,
                "model_count": model_count,
                "message": f"Ollama is running with {model_count} model(s) available"
            }
        except Exception as e:
            error_msg = str(e)
            if "connection" in error_msg.lower() or "refused" in error_msg.lower():
                return {
                    "online": False,
                    "model_count": 0,
                    "message": "Ollama is not running. Start it with 'ollama serve'",
                    "error": error_msg,
                    "setup_hint": "Install Ollama from https://ollama.com and run 'ollama pull llama3.2'"
                }
            return {
                "online": False,
                "model_count": 0,
                "message": f"Ollama error: {error_msg}",
                "error": error_msg
            }
    
    @classmethod
    def get_available_models(cls) -> dict:
        """
        Fetch list of available Ollama models with detailed metadata.
        
        Returns:
            dict with 'models' list and 'status' info
        """
        try:
            response = ollama.list()
            models = []
            
            for model in response.get("models", []):
                details = model.get("details", {})
                name = model.get("name", "unknown")
                size_bytes = model.get("size", 0)
                
                models.append({
                    "name": name,
                    "size": size_bytes,
                    "size_human": cls._format_size(size_bytes),
                    "modified_at": model.get("modified_at", ""),
                    "family": details.get("family", "unknown"),
                    "parameter_size": details.get("parameter_size", "Unknown"),
                    "quantization": cls._extract_quantization(name, details),
                    "format": details.get("format", "unknown"),
                    "families": details.get("families", []),
                    "is_available": True,
                })
            
            # Sort by preference order, then alphabetically
            def sort_key(m):
                name_lower = m["name"].lower()
                for idx, pref in enumerate(cls.PREFERRED_MODELS):
                    if pref in name_lower:
                        return (0, idx, m["name"])
                return (1, 999, m["name"])
            
            models.sort(key=sort_key)
            
            # Determine recommended model
            recommended = None
            for pref in cls.PREFERRED_MODELS:
                for model in models:
                    if pref in model["name"].lower():
                        recommended = model["name"]
                        break
                if recommended:
                    break
            
            if not recommended and models:
                recommended = models[0]["name"]
            
            return {
                "models": models,
                "status": {
                    "online": True,
                    "count": len(models),
                    "recommended": recommended,
                },
            }
            
        except Exception as e:
            error_msg = str(e)
            is_connection_error = "connection" in error_msg.lower() or "refused" in error_msg.lower()
            
            # Return placeholder models with offline status
            placeholder_models = [
                {
                    "name": m,
                    "size": 0,
                    "size_human": "N/A",
                    "modified_at": "",
                    "family": "default",
                    "parameter_size": "Unknown",
                    "quantization": "Unknown",
                    "format": "unknown",
                    "families": [],
                    "is_available": False,
                }
                for m in cls.DEFAULT_MODELS
            ]
            
            return {
                "models": placeholder_models,
                "status": {
                    "online": False,
                    "count": 0,
                    "recommended": None,
                    "error": error_msg,
                    "setup_hint": "Install Ollama from https://ollama.com and run 'ollama serve'" if is_connection_error else None,
                },
            }
    
    @classmethod
    def analyze_comparison(cls, model_name: str, comparison_summary: dict, 
                          user_prompt: str) -> dict:
        """
        Use AI to analyze comparison results and answer user questions.
        
        Args:
            model_name: The Ollama model to use
            comparison_summary: The comparison results dictionary
            user_prompt: The user's question or analysis request
        """
        # Use centralized system prompt from config
        system_prompt = AI_SYSTEM_PROMPTS["analysis"]
        
        # Prepare context from comparison
        context = cls._format_comparison_context(comparison_summary)
        
        full_prompt = f"""Based on this data comparison analysis:

{context}

User Question: {user_prompt}

Provide a detailed, actionable response:"""
        
        try:
            response = ollama.chat(
                model=model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": full_prompt},
                ],
            )
            
            return {
                "success": True,
                "response": response["message"]["content"],
                "model": model_name,
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "model": model_name,
            }
    
    @classmethod
    def analyze_comparison_stream(cls, model_name: str, comparison_summary: dict, 
                                  user_prompt: str) -> Generator[str, None, None]:
        """
        Stream AI analysis response token by token for SSE.
        
        Args:
            model_name: The Ollama model to use
            comparison_summary: The comparison results dictionary
            user_prompt: The user's question or analysis request
            
        Yields:
            Response tokens as they are generated
        """
        # Use centralized system prompt from config
        system_prompt = AI_SYSTEM_PROMPTS["analysis"]
        
        # Prepare context from comparison
        context = cls._format_comparison_context(comparison_summary)
        
        full_prompt = f"""Based on this data comparison analysis:

{context}

User Question: {user_prompt}

Provide a detailed, actionable response:"""
        
        try:
            stream = ollama.chat(
                model=model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": full_prompt},
                ],
                stream=True,
            )
            
            for chunk in stream:
                if "message" in chunk and "content" in chunk["message"]:
                    yield chunk["message"]["content"]
        except Exception as e:
            yield f"\n\n[Error: {str(e)}]"
    
    @classmethod
    def suggest_join_columns(cls, model_name: str, df1_columns: list[str], 
                            df2_columns: list[str]) -> dict:
        """Use AI to suggest the best join columns for comparison."""
        prompt = f"""Given these two datasets with the following columns:

Dataset A columns: {', '.join(df1_columns)}

Dataset B columns: {', '.join(df2_columns)}

Identify the best column(s) to use as unique identifiers for comparing rows between these datasets.
Consider columns that appear to be:
1. Primary keys or IDs
2. Document identifiers (DocID, BatesNumber, etc.)
3. Unique record identifiers

Return your answer as a JSON object with this structure:
{{"suggested_columns": ["column1", "column2"], "reasoning": "explanation"}}"""
        
        try:
            response = ollama.chat(
                model=model_name,
                messages=[{"role": "user", "content": prompt}],
            )
            
            content = response["message"]["content"]
            # Try to extract JSON from response
            try:
                import re
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    result = json.loads(json_match.group())
                    return {"success": True, **result}
            except (json.JSONDecodeError, AttributeError, KeyError):
                # JSON extraction failed, fall through to return raw content
                pass
            
            return {
                "success": True,
                "suggested_columns": [],
                "reasoning": content,
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }
    
    @classmethod
    def explain_differences(cls, model_name: str, differences: list[dict], 
                           column_name: str) -> dict:
        """Get AI explanation for specific column differences."""
        sample_diffs = differences[:20]  # Limit samples
        
        prompt = f"""Analyze these differences found in the column '{column_name}' between two datasets:

{json.dumps(sample_diffs, indent=2)}

Provide insights on:
1. Pattern of differences (are they consistent transformations?)
2. Potential causes (encoding, formatting, data entry errors?)
3. Which dataset appears to have the correct/preferred format
4. Recommendations for data reconciliation"""
        
        try:
            response = ollama.chat(
                model=model_name,
                messages=[{"role": "user", "content": prompt}],
            )
            
            return {
                "success": True,
                "explanation": response["message"]["content"],
                "samples_analyzed": len(sample_diffs),
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }
    
    @classmethod
    def _format_comparison_context(cls, summary: dict) -> str:
        """Format comparison summary for AI context."""
        lines = []
        
        if "summary" in summary:
            s = summary["summary"]
            lines.append(f"## Dataset Overview")
            lines.append(f"- {s.get('df1_name', 'File A')}: {s.get('df1_rows', 0)} rows, {s.get('df1_columns', 0)} columns")
            lines.append(f"- {s.get('df2_name', 'File B')}: {s.get('df2_rows', 0)} rows, {s.get('df2_columns', 0)} columns")
            lines.append(f"- Common rows matched: {s.get('common_rows', 0)}")
        
        if "columns" in summary:
            c = summary["columns"]
            lines.append(f"\n## Column Differences")
            lines.append(f"- Columns only in first file: {c.get('only_in_df1', [])}")
            lines.append(f"- Columns only in second file: {c.get('only_in_df2', [])}")
            lines.append(f"- Columns with mismatched data: {c.get('mismatched', [])}")
        
        if "rows" in summary:
            r = summary["rows"]
            lines.append(f"\n## Row Differences")
            lines.append(f"- Rows only in first file: {r.get('only_in_df1_count', 0)}")
            lines.append(f"- Rows only in second file: {r.get('only_in_df2_count', 0)}")
        
        if "column_stats" in summary:
            lines.append(f"\n## Column Statistics")
            for stat in summary["column_stats"][:10]:
                if stat.get("mismatch_count", 0) > 0:
                    lines.append(f"- {stat['column']}: {stat['mismatch_count']} mismatches")
        
        return "\n".join(lines)

