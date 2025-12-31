"""
Schema Analyzer Service - Deep schema/structure comparison across files.
Detects column mismatches, type compatibility, and suggests mappings.
"""
import pandas as pd
import numpy as np
from typing import Optional
from difflib import SequenceMatcher
from collections import defaultdict
import re


class SchemaAnalyzer:
    """
    Analyzes and compares schemas across multiple dataframes.
    Provides:
    - Column name matching (exact, fuzzy, case-insensitive)
    - Data type compatibility analysis
    - Format validation (dates, emails, etc.)
    - Column mapping suggestions
    """
    
    # Common type compatibility groups
    TYPE_COMPATIBILITY = {
        'numeric': ['int64', 'int32', 'int16', 'int8', 'float64', 'float32', 'float16'],
        'integer': ['int64', 'int32', 'int16', 'int8'],
        'float': ['float64', 'float32', 'float16'],
        'string': ['object', 'string', 'str'],
        'datetime': ['datetime64[ns]', 'datetime64', 'date'],
        'boolean': ['bool', 'boolean'],
        'category': ['category'],
    }
    
    # Common column name patterns
    COMMON_PATTERNS = {
        'id': [r'id$', r'_id$', r'^id_', r'identifier', r'key$'],
        'name': [r'name$', r'_name$', r'^name_', r'title', r'label'],
        'date': [r'date$', r'_date$', r'^date_', r'_at$', r'timestamp', r'time$', r'created', r'modified'],
        'amount': [r'amount', r'total', r'sum', r'value', r'price', r'cost'],
        'count': [r'count', r'num', r'qty', r'quantity'],
        'email': [r'email', r'e_mail', r'mail'],
        'phone': [r'phone', r'tel', r'mobile', r'cell'],
        'address': [r'address', r'addr', r'street', r'city', r'state', r'zip', r'postal'],
    }
    
    def __init__(self, dataframes: dict[str, pd.DataFrame]):
        """
        Initialize with dictionary of dataframes.
        
        Args:
            dataframes: Dict mapping filename -> DataFrame
        """
        self.dataframes = dataframes
        self.file_names = list(dataframes.keys())
        self._analysis: Optional[dict] = None
    
    def analyze(self) -> dict:
        """
        Perform comprehensive schema analysis.
        
        Returns:
            Complete schema analysis results
        """
        # Get all column info
        schemas = {}
        for name, df in self.dataframes.items():
            schemas[name] = self._extract_schema(df)
        
        # Analyze column alignment
        column_alignment = self._analyze_column_alignment(schemas)
        
        # Detect type compatibility
        type_analysis = self._analyze_type_compatibility(schemas)
        
        # Generate column mapping suggestions
        mapping_suggestions = self._suggest_column_mappings(schemas)
        
        # Identify potential issues
        issues = self._identify_issues(schemas, type_analysis)
        
        # Generate format analysis for common columns
        format_analysis = self._analyze_formats()
        
        self._analysis = {
            "schemas": schemas,
            "column_alignment": column_alignment,
            "type_compatibility": type_analysis,
            "mapping_suggestions": mapping_suggestions,
            "format_analysis": format_analysis,
            "issues": issues,
            "summary": self._generate_summary(schemas, column_alignment, issues),
        }
        
        return self._analysis
    
    def _extract_schema(self, df: pd.DataFrame) -> dict:
        """Extract detailed schema from a dataframe."""
        schema = {
            "columns": {},
            "row_count": len(df),
            "column_count": len(df.columns),
            "memory_usage": df.memory_usage(deep=True).sum(),
        }
        
        for col in df.columns:
            col_info = {
                "dtype": str(df[col].dtype),
                "nullable": bool(df[col].isnull().any()),
                "null_count": int(df[col].isnull().sum()),
                "null_percentage": round(df[col].isnull().sum() / len(df) * 100, 2) if len(df) > 0 else 0,
                "unique_count": int(df[col].nunique()),
                "unique_percentage": round(df[col].nunique() / len(df) * 100, 2) if len(df) > 0 else 0,
            }
            
            # Add type-specific info
            if pd.api.types.is_numeric_dtype(df[col]):
                col_info["min"] = float(df[col].min()) if not df[col].isnull().all() else None
                col_info["max"] = float(df[col].max()) if not df[col].isnull().all() else None
                col_info["mean"] = float(df[col].mean()) if not df[col].isnull().all() else None
            elif pd.api.types.is_string_dtype(df[col]) or df[col].dtype == 'object':
                sample = df[col].dropna()
                if len(sample) > 0:
                    col_info["avg_length"] = round(sample.astype(str).str.len().mean(), 2)
                    col_info["max_length"] = int(sample.astype(str).str.len().max())
                    col_info["sample_values"] = sample.head(5).tolist()
            
            schema["columns"][col] = col_info
        
        return schema
    
    def _analyze_column_alignment(self, schemas: dict) -> dict:
        """Analyze column presence and alignment across files."""
        all_columns = set()
        column_presence = defaultdict(set)
        
        for file_name, schema in schemas.items():
            for col in schema["columns"]:
                all_columns.add(col)
                column_presence[col].add(file_name)
        
        # Categorize columns
        columns_in_all = []
        columns_in_some = {}
        file_unique = {name: [] for name in self.file_names}
        
        for col in all_columns:
            files = column_presence[col]
            if len(files) == len(self.file_names):
                columns_in_all.append(col)
            elif len(files) == 1:
                file_name = list(files)[0]
                file_unique[file_name].append(col)
            else:
                columns_in_some[col] = list(files)
        
        return {
            "all_columns": list(all_columns),
            "columns_in_all_files": sorted(columns_in_all),
            "columns_in_some_files": columns_in_some,
            "file_unique_columns": file_unique,
            "column_presence_matrix": {
                col: {name: col in schemas[name]["columns"] 
                      for name in self.file_names}
                for col in all_columns
            },
        }
    
    def _analyze_type_compatibility(self, schemas: dict) -> dict:
        """Analyze data type compatibility across files."""
        all_columns = set()
        for schema in schemas.values():
            all_columns.update(schema["columns"].keys())
        
        type_info = {}
        for col in all_columns:
            col_types = {}
            for file_name, schema in schemas.items():
                if col in schema["columns"]:
                    col_types[file_name] = schema["columns"][col]["dtype"]
            
            if len(col_types) > 1:
                unique_types = set(col_types.values())
                compatible = self._check_type_compatibility(unique_types)
                
                type_info[col] = {
                    "types": col_types,
                    "unique_types": list(unique_types),
                    "is_compatible": compatible,
                    "compatibility_group": self._get_compatibility_group(unique_types),
                }
        
        # Summarize
        compatible_columns = [col for col, info in type_info.items() if info["is_compatible"]]
        incompatible_columns = [col for col, info in type_info.items() if not info["is_compatible"]]
        
        return {
            "column_types": type_info,
            "compatible_columns": compatible_columns,
            "incompatible_columns": incompatible_columns,
            "compatibility_matrix": self._build_compatibility_matrix(type_info),
        }
    
    def _check_type_compatibility(self, types: set) -> bool:
        """Check if a set of types are compatible."""
        types_normalized = {t.lower() for t in types}
        
        for group_types in self.TYPE_COMPATIBILITY.values():
            group_set = set(group_types)
            if types_normalized.issubset(group_set):
                return True
        
        # Check if all are numeric (int + float are compatible)
        numeric_types = set(self.TYPE_COMPATIBILITY['integer'] + 
                          self.TYPE_COMPATIBILITY['float'])
        if types_normalized.issubset(numeric_types):
            return True
        
        return len(types_normalized) == 1
    
    def _get_compatibility_group(self, types: set) -> str:
        """Get the compatibility group for a set of types."""
        types_normalized = {t.lower() for t in types}
        
        for group_name, group_types in self.TYPE_COMPATIBILITY.items():
            if types_normalized.issubset(set(group_types)):
                return group_name
        
        # Check numeric (int + float)
        numeric_types = set(self.TYPE_COMPATIBILITY['integer'] + 
                          self.TYPE_COMPATIBILITY['float'])
        if types_normalized.issubset(numeric_types):
            return 'numeric'
        
        return 'mixed'
    
    def _build_compatibility_matrix(self, type_info: dict) -> dict:
        """Build a compatibility matrix for visualization."""
        matrix = {
            "columns": list(type_info.keys()),
            "files": self.file_names,
            "data": [],
        }
        
        for col, info in type_info.items():
            row = {
                "column": col,
                "compatible": info["is_compatible"],
            }
            for file_name in self.file_names:
                row[file_name] = info["types"].get(file_name, "-")
            matrix["data"].append(row)
        
        return matrix
    
    def _suggest_column_mappings(self, schemas: dict) -> dict:
        """Suggest column mappings for misaligned columns."""
        suggestions = []
        
        # Get columns unique to each file
        all_columns_by_file = {
            name: set(schema["columns"].keys())
            for name, schema in schemas.items()
        }
        
        # For each pair of files, find potential mappings
        for i, file1 in enumerate(self.file_names):
            for file2 in self.file_names[i+1:]:
                cols1 = all_columns_by_file[file1]
                cols2 = all_columns_by_file[file2]
                
                # Find columns unique to each file
                unique_to_1 = cols1 - cols2
                unique_to_2 = cols2 - cols1
                
                # Try to match unique columns
                for col1 in unique_to_1:
                    for col2 in unique_to_2:
                        similarity = self._calculate_column_similarity(
                            col1, col2, schemas[file1], schemas[file2]
                        )
                        
                        if similarity["score"] >= 0.6:
                            suggestions.append({
                                "file1": file1,
                                "column1": col1,
                                "file2": file2,
                                "column2": col2,
                                "similarity_score": similarity["score"],
                                "match_reasons": similarity["reasons"],
                            })
        
        # Sort by similarity score
        suggestions.sort(key=lambda x: x["similarity_score"], reverse=True)
        
        return {
            "suggestions": suggestions[:20],  # Top 20 suggestions
            "total_suggestions": len(suggestions),
        }
    
    def _calculate_column_similarity(self, col1: str, col2: str,
                                    schema1: dict, schema2: dict) -> dict:
        """Calculate similarity score between two columns."""
        score = 0.0
        reasons = []
        
        # Name similarity (fuzzy match)
        name_ratio = SequenceMatcher(None, col1.lower(), col2.lower()).ratio()
        if name_ratio >= 0.8:
            score += 0.4
            reasons.append(f"Name similarity: {name_ratio:.2f}")
        elif name_ratio >= 0.6:
            score += 0.2
            reasons.append(f"Name similarity: {name_ratio:.2f}")
        
        # Check if same pattern type (e.g., both look like IDs)
        pattern1 = self._detect_column_pattern(col1)
        pattern2 = self._detect_column_pattern(col2)
        if pattern1 and pattern2 and pattern1 == pattern2:
            score += 0.3
            reasons.append(f"Same pattern type: {pattern1}")
        
        # Type compatibility
        col1_info = schema1["columns"].get(col1, {})
        col2_info = schema2["columns"].get(col2, {})
        
        if col1_info and col2_info:
            dtype1 = col1_info.get("dtype", "")
            dtype2 = col2_info.get("dtype", "")
            
            if self._check_type_compatibility({dtype1, dtype2}):
                score += 0.2
                reasons.append("Compatible data types")
            
            # Similar uniqueness
            uniq1 = col1_info.get("unique_percentage", 0)
            uniq2 = col2_info.get("unique_percentage", 0)
            if abs(uniq1 - uniq2) < 10:
                score += 0.1
                reasons.append("Similar uniqueness distribution")
        
        return {"score": min(score, 1.0), "reasons": reasons}
    
    def _detect_column_pattern(self, column_name: str) -> Optional[str]:
        """Detect what type of data a column likely contains based on name."""
        col_lower = column_name.lower()
        
        for pattern_type, patterns in self.COMMON_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, col_lower):
                    return pattern_type
        
        return None
    
    def _identify_issues(self, schemas: dict, type_analysis: dict) -> list:
        """Identify potential schema issues."""
        issues = []
        
        # Type incompatibility issues
        for col in type_analysis.get("incompatible_columns", []):
            col_info = type_analysis["column_types"].get(col, {})
            issues.append({
                "type": "type_incompatibility",
                "severity": "high",
                "column": col,
                "message": f"Column '{col}' has incompatible types across files",
                "details": col_info.get("types", {}),
            })
        
        # High null percentage warnings
        for file_name, schema in schemas.items():
            for col, info in schema["columns"].items():
                if info.get("null_percentage", 0) > 50:
                    issues.append({
                        "type": "high_null_percentage",
                        "severity": "medium",
                        "file": file_name,
                        "column": col,
                        "message": f"Column '{col}' in '{file_name}' has {info['null_percentage']}% null values",
                    })
        
        # Columns with very different uniqueness across files
        all_columns = set()
        for schema in schemas.values():
            all_columns.update(schema["columns"].keys())
        
        for col in all_columns:
            uniq_values = []
            for file_name, schema in schemas.items():
                if col in schema["columns"]:
                    uniq_values.append(schema["columns"][col].get("unique_percentage", 0))
            
            if len(uniq_values) > 1 and max(uniq_values) - min(uniq_values) > 50:
                issues.append({
                    "type": "uniqueness_mismatch",
                    "severity": "medium",
                    "column": col,
                    "message": f"Column '{col}' has very different uniqueness across files",
                    "details": {name: schemas[name]["columns"][col]["unique_percentage"]
                              for name in self.file_names if col in schemas[name]["columns"]},
                })
        
        return issues
    
    def _analyze_formats(self) -> dict:
        """Analyze data formats for potential standardization."""
        format_analysis = {}
        
        # Find common string columns
        common_columns = set()
        for schema in self._extract_schema(list(self.dataframes.values())[0])["columns"]:
            is_common = all(
                schema in self._extract_schema(df)["columns"]
                for df in self.dataframes.values()
            )
            if is_common:
                common_columns.add(schema)
        
        for col in common_columns:
            col_formats = {}
            for file_name, df in self.dataframes.items():
                if col in df.columns and df[col].dtype == 'object':
                    sample = df[col].dropna().head(100)
                    col_formats[file_name] = self._detect_format_patterns(sample)
            
            if col_formats:
                format_analysis[col] = col_formats
        
        return format_analysis
    
    def _detect_format_patterns(self, series: pd.Series) -> dict:
        """Detect format patterns in a series."""
        patterns = {
            "date_formats": [],
            "case_pattern": None,
            "has_leading_zeros": False,
            "common_prefixes": [],
        }
        
        if len(series) == 0:
            return patterns
        
        sample = series.astype(str)
        
        # Check case pattern
        upper_count = sum(1 for s in sample if s.isupper())
        lower_count = sum(1 for s in sample if s.islower())
        
        if upper_count > len(sample) * 0.8:
            patterns["case_pattern"] = "UPPER"
        elif lower_count > len(sample) * 0.8:
            patterns["case_pattern"] = "lower"
        else:
            patterns["case_pattern"] = "Mixed"
        
        # Check for leading zeros
        numeric_like = sample[sample.str.match(r'^\d+$', na=False)]
        if len(numeric_like) > 0:
            has_leading = any(s.startswith('0') and len(s) > 1 for s in numeric_like)
            patterns["has_leading_zeros"] = has_leading
        
        return patterns
    
    def _generate_summary(self, schemas: dict, alignment: dict, issues: list) -> dict:
        """Generate summary of schema analysis."""
        high_issues = [i for i in issues if i.get("severity") == "high"]
        medium_issues = [i for i in issues if i.get("severity") == "medium"]
        
        return {
            "file_count": len(self.file_names),
            "total_unique_columns": len(alignment["all_columns"]),
            "columns_in_all_files": len(alignment["columns_in_all_files"]),
            "columns_in_some_files": len(alignment["columns_in_some_files"]),
            "schema_compatibility": "compatible" if len(high_issues) == 0 else "incompatible",
            "issue_count": {
                "high": len(high_issues),
                "medium": len(medium_issues),
                "total": len(issues),
            },
            "file_details": {
                name: {
                    "columns": schema["column_count"],
                    "rows": schema["row_count"],
                }
                for name, schema in schemas.items()
            },
        }

