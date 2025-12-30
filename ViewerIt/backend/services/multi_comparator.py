"""
Multi-File Comparator Service - Compare 3+ files simultaneously.
Provides cross-file reconciliation and comprehensive difference analysis.
"""
import pandas as pd
import numpy as np
from typing import Optional
from collections import defaultdict
from itertools import combinations


class MultiFileComparator:
    """
    Compares multiple (3+) dataframes simultaneously.
    Unlike pairwise comparison, this identifies:
    - Records present in ALL files
    - Records in N of M files  
    - File-specific records
    - Cross-file reconciliation matrix
    """
    
    def __init__(self, dataframes: dict[str, pd.DataFrame]):
        """
        Initialize with a dictionary of dataframes.
        
        Args:
            dataframes: Dict mapping filename -> DataFrame
        """
        if len(dataframes) < 2:
            raise ValueError("At least 2 dataframes required for comparison")
        
        self.dataframes = dataframes
        self.file_names = list(dataframes.keys())
        self._results: Optional[dict] = None
    
    def compare(self, join_columns: list[str], 
                ignore_columns: Optional[list[str]] = None) -> dict:
        """
        Perform multi-file comparison.
        
        Args:
            join_columns: Columns to use as unique identifiers
            ignore_columns: Columns to exclude from comparison
            
        Returns:
            Comprehensive comparison results
        """
        # Prepare dataframes
        dfs = {}
        for name, df in self.dataframes.items():
            df_copy = df.copy()
            if ignore_columns:
                cols_to_drop = [c for c in ignore_columns if c in df_copy.columns]
                df_copy = df_copy.drop(columns=cols_to_drop, errors='ignore')
            dfs[name] = df_copy
        
        # Create composite key for each dataframe
        keyed_dfs = {}
        for name, df in dfs.items():
            if not all(col in df.columns for col in join_columns):
                missing = [col for col in join_columns if col not in df.columns]
                raise ValueError(f"File '{name}' missing join columns: {missing}")
            
            # Create composite key
            df_keyed = df.copy()
            df_keyed['_composite_key'] = df_keyed[join_columns].astype(str).agg('|'.join, axis=1)
            keyed_dfs[name] = df_keyed
        
        # Get all unique keys across all files
        all_keys = set()
        key_to_files = defaultdict(set)
        key_to_data = defaultdict(dict)
        
        for name, df in keyed_dfs.items():
            for _, row in df.iterrows():
                key = row['_composite_key']
                all_keys.add(key)
                key_to_files[key].add(name)
                key_to_data[key][name] = row.drop('_composite_key').to_dict()
        
        # Categorize records
        records_in_all = []
        records_in_some = []
        records_in_one = []
        file_exclusive_records = {name: [] for name in self.file_names}
        
        n_files = len(self.file_names)
        
        for key in all_keys:
            files_with_key = key_to_files[key]
            record_info = {
                'key': key,
                'files': list(files_with_key),
                'file_count': len(files_with_key),
                'data': key_to_data[key],
            }
            
            if len(files_with_key) == n_files:
                records_in_all.append(record_info)
            elif len(files_with_key) == 1:
                records_in_one.append(record_info)
                file_exclusive_records[list(files_with_key)[0]].append(record_info)
            else:
                records_in_some.append(record_info)
        
        # Build presence matrix
        presence_matrix = self._build_presence_matrix(all_keys, key_to_files)
        
        # Analyze value differences for records in multiple files
        value_differences = self._analyze_value_differences(
            records_in_all + records_in_some, 
            join_columns
        )
        
        # Column analysis across files
        column_analysis = self._analyze_columns(dfs)
        
        # Generate summary statistics
        summary = self._generate_summary(
            all_keys, records_in_all, records_in_some, 
            records_in_one, file_exclusive_records
        )
        
        self._results = {
            "summary": summary,
            "records_in_all_files": {
                "count": len(records_in_all),
                "samples": records_in_all[:20],  # Limit samples
            },
            "records_in_some_files": {
                "count": len(records_in_some),
                "by_file_count": self._group_by_file_count(records_in_some),
                "samples": records_in_some[:20],
            },
            "records_in_one_file": {
                "count": len(records_in_one),
                "by_file": {name: len(recs) for name, recs in file_exclusive_records.items()},
                "samples": records_in_one[:20],
            },
            "presence_matrix": presence_matrix,
            "value_differences": value_differences,
            "column_analysis": column_analysis,
            "venn_data": self._generate_venn_data(key_to_files),
        }
        
        return self._results
    
    def _build_presence_matrix(self, all_keys: set, 
                               key_to_files: dict) -> dict:
        """Build a matrix showing record presence across files."""
        matrix = {
            "headers": ["Key"] + self.file_names,
            "rows": [],
        }
        
        # Limit to first 100 for display
        for key in list(all_keys)[:100]:
            row = [key] + [key in key_to_files[key] and name in key_to_files[key] 
                          for name in self.file_names]
            # Simplify: check if each file has this key
            row = [key] + [name in key_to_files[key] for name in self.file_names]
            matrix["rows"].append(row)
        
        return matrix
    
    def _analyze_value_differences(self, records: list, 
                                   join_columns: list[str]) -> dict:
        """Analyze value differences for records present in multiple files."""
        differences = defaultdict(list)
        
        for record in records:
            if record['file_count'] < 2:
                continue
            
            files = record['files']
            data = record['data']
            
            # Get all columns (excluding join columns for value comparison)
            all_cols = set()
            for file_data in data.values():
                all_cols.update(file_data.keys())
            
            compare_cols = [c for c in all_cols if c not in join_columns]
            
            for col in compare_cols:
                values = {}
                for file_name in files:
                    if col in data.get(file_name, {}):
                        values[file_name] = data[file_name][col]
                
                # Check if values differ
                unique_values = set(str(v) for v in values.values())
                if len(unique_values) > 1:
                    differences[col].append({
                        'key': record['key'],
                        'values': values,
                    })
        
        # Summarize differences
        return {
            col: {
                'mismatch_count': len(diffs),
                'samples': diffs[:10],
            }
            for col, diffs in differences.items()
        }
    
    def _analyze_columns(self, dfs: dict[str, pd.DataFrame]) -> dict:
        """Analyze column presence and types across files."""
        all_columns = set()
        column_presence = defaultdict(set)
        column_types = defaultdict(dict)
        
        for name, df in dfs.items():
            for col in df.columns:
                all_columns.add(col)
                column_presence[col].add(name)
                column_types[col][name] = str(df[col].dtype)
        
        columns_in_all = [col for col in all_columns 
                        if len(column_presence[col]) == len(self.file_names)]
        columns_in_some = [col for col in all_columns 
                         if 1 < len(column_presence[col]) < len(self.file_names)]
        
        # Identify columns unique to each file
        file_unique_columns = {}
        for name in self.file_names:
            unique_cols = [col for col in all_columns 
                         if column_presence[col] == {name}]
            file_unique_columns[name] = unique_cols
        
        # Identify type mismatches
        type_mismatches = {}
        for col in columns_in_all + columns_in_some:
            types = column_types[col]
            unique_types = set(types.values())
            if len(unique_types) > 1:
                type_mismatches[col] = types
        
        return {
            "all_columns": list(all_columns),
            "columns_in_all_files": columns_in_all,
            "columns_in_some_files": {
                col: list(column_presence[col]) for col in columns_in_some
            },
            "file_unique_columns": file_unique_columns,
            "column_types": dict(column_types),
            "type_mismatches": type_mismatches,
        }
    
    def _generate_summary(self, all_keys: set, records_in_all: list,
                         records_in_some: list, records_in_one: list,
                         file_exclusive: dict) -> dict:
        """Generate summary statistics."""
        return {
            "total_unique_records": len(all_keys),
            "file_count": len(self.file_names),
            "file_names": self.file_names,
            "records_in_all_files": len(records_in_all),
            "records_in_multiple_files": len(records_in_all) + len(records_in_some),
            "records_in_single_file": len(records_in_one),
            "file_record_counts": {
                name: len(self.dataframes[name]) 
                for name in self.file_names
            },
            "file_exclusive_counts": {
                name: len(recs) for name, recs in file_exclusive.items()
            },
            "overlap_percentage": round(
                len(records_in_all) / len(all_keys) * 100 if all_keys else 0, 2
            ),
        }
    
    def _group_by_file_count(self, records: list) -> dict:
        """Group records by the number of files they appear in."""
        groups = defaultdict(list)
        for record in records:
            groups[record['file_count']].append(record)
        
        return {
            count: {
                'count': len(recs),
                'samples': recs[:5],
            }
            for count, recs in sorted(groups.items())
        }
    
    def _generate_venn_data(self, key_to_files: dict) -> dict:
        """Generate data for Venn diagram visualization."""
        if len(self.file_names) > 5:
            return {"error": "Venn diagram not supported for more than 5 files"}
        
        # Count records in each combination
        combination_counts = defaultdict(int)
        
        for key, files in key_to_files.items():
            # Create a sorted tuple of file names for this record
            combo = tuple(sorted(files))
            combination_counts[combo] += 1
        
        # Format for visualization
        venn_sets = []
        for combo, count in combination_counts.items():
            venn_sets.append({
                "sets": list(combo),
                "size": count,
            })
        
        return {
            "file_names": self.file_names,
            "sets": venn_sets,
        }
    
    def get_reconciliation_report(self) -> dict:
        """Generate a detailed reconciliation report."""
        if not self._results:
            raise ValueError("Run compare() first")
        
        report = {
            "summary": self._results["summary"],
            "recommendations": [],
            "action_items": [],
        }
        
        summary = self._results["summary"]
        
        # Generate recommendations
        if summary["records_in_single_file"] > 0:
            report["recommendations"].append({
                "type": "missing_records",
                "message": f"{summary['records_in_single_file']} records exist in only one file",
                "action": "Review file-exclusive records for potential data sync issues",
            })
        
        if self._results["value_differences"]:
            diff_cols = list(self._results["value_differences"].keys())
            report["recommendations"].append({
                "type": "value_mismatches",
                "message": f"Value differences found in {len(diff_cols)} column(s): {diff_cols}",
                "action": "Review and reconcile value differences",
            })
        
        if self._results["column_analysis"]["type_mismatches"]:
            report["recommendations"].append({
                "type": "type_mismatches",
                "message": "Data type inconsistencies found across files",
                "columns": list(self._results["column_analysis"]["type_mismatches"].keys()),
                "action": "Standardize data types before merging",
            })
        
        return report
    
    def export_differences(self, format: str = "records") -> pd.DataFrame:
        """Export differences as a DataFrame for further analysis."""
        if not self._results:
            raise ValueError("Run compare() first")
        
        records = []
        
        # Add records in single file
        for record in self._results["records_in_one_file"]["samples"]:
            records.append({
                "key": record["key"],
                "status": "single_file",
                "files": ", ".join(record["files"]),
                "file_count": 1,
            })
        
        # Add records in some files
        for record in self._results["records_in_some_files"]["samples"]:
            records.append({
                "key": record["key"],
                "status": "partial_overlap",
                "files": ", ".join(record["files"]),
                "file_count": record["file_count"],
            })
        
        return pd.DataFrame(records)

