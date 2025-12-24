"""
AI Service - Ollama integration for intelligent data analysis.
"""
import ollama
from typing import Optional
import json


class AIService:
    """Handles AI-powered analysis using Ollama."""
    
    DEFAULT_MODELS = ["llama3.2", "mistral", "phi3", "gemma2"]
    
    @classmethod
    def get_available_models(cls) -> list[dict]:
        """Fetch list of available Ollama models."""
        try:
            response = ollama.list()
            models = []
            for model in response.get("models", []):
                models.append({
                    "name": model.get("name", "unknown"),
                    "size": model.get("size", 0),
                    "modified_at": model.get("modified_at", ""),
                    "family": model.get("details", {}).get("family", "unknown"),
                })
            return models if models else [{"name": m, "size": 0, "family": "default"} for m in cls.DEFAULT_MODELS]
        except Exception as e:
            # Return defaults if Ollama is not running
            return [{"name": m, "size": 0, "family": "default", "error": str(e)} for m in cls.DEFAULT_MODELS]
    
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
        system_prompt = """You are an expert data analyst specializing in eDiscovery and legal data comparison. 
You analyze data differences between datasets and provide actionable insights.
Always be precise about numbers and specific about which dataset has issues.
Format your responses with clear sections and bullet points for readability."""
        
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
            except:
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

