"""
Chunked Processor Service - Handles large file processing efficiently.
Uses chunked reading and parallel processing for performance.

Performance optimized with optional Rust acceleration for set operations.
"""
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Optional, Generator, Callable
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

logger = logging.getLogger(__name__)

# Configuration
CHUNK_SIZE = 50000  # Rows per chunk
LARGE_FILE_THRESHOLD = 100000  # Rows to trigger chunked processing
MAX_WORKERS = 4  # Parallel workers

# Try to import Rust acceleration module
try:
    from viewerit_core import FastIntersector
    RUST_AVAILABLE = True
    logger.info("viewerit_core Rust extension loaded for chunked processing")
except ImportError:
    RUST_AVAILABLE = False
    logger.debug("viewerit_core not available for chunked processing - using Python fallback")


class ChunkedProcessor:
    """
    Processes large files in chunks to avoid memory issues.
    Supports chunked reading, parallel processing, and streaming aggregation.
    
    Uses Rust acceleration when available for set operations.
    """
    
    def __init__(self, chunk_size: int = CHUNK_SIZE):
        self.chunk_size = chunk_size
        self._use_rust = RUST_AVAILABLE
    
    def is_large_file(self, file_path: Path, threshold: int = LARGE_FILE_THRESHOLD) -> bool:
        """
        Check if a file is likely large enough to require chunked processing.
        Uses file size heuristic rather than loading the file.
        """
        file_size = file_path.stat().st_size
        # Rough estimate: 100 bytes per row average
        estimated_rows = file_size / 100
        return estimated_rows > threshold
    
    def read_csv_chunked(self, file_path: Path, 
                         encoding: str = 'utf-8',
                         **kwargs) -> Generator[pd.DataFrame, None, None]:
        """
        Read CSV file in chunks, yielding each chunk.
        
        Args:
            file_path: Path to CSV file
            encoding: File encoding
            **kwargs: Additional arguments for pd.read_csv
            
        Yields:
            DataFrame chunks
        """
        try:
            reader = pd.read_csv(
                file_path,
                encoding=encoding,
                chunksize=self.chunk_size,
                low_memory=True,
                **kwargs
            )
            for chunk in reader:
                yield chunk
        except UnicodeDecodeError:
            # Fallback to latin-1
            reader = pd.read_csv(
                file_path,
                encoding='latin-1',
                chunksize=self.chunk_size,
                low_memory=True,
                **kwargs
            )
            for chunk in reader:
                yield chunk
    
    def process_chunked(self, file_path: Path,
                        processor: Callable[[pd.DataFrame], dict],
                        aggregator: Callable[[list[dict]], dict]) -> dict:
        """
        Process a large file in chunks with custom processor and aggregator.
        
        Args:
            file_path: Path to file
            processor: Function to process each chunk, returns partial result
            aggregator: Function to combine partial results
            
        Returns:
            Aggregated result
        """
        partial_results = []
        
        for chunk in self.read_csv_chunked(file_path):
            result = processor(chunk)
            partial_results.append(result)
        
        return aggregator(partial_results)
    
    def get_chunked_statistics(self, file_path: Path) -> dict:
        """
        Get statistics for a large file using chunked processing.
        """
        def process_chunk(chunk: pd.DataFrame) -> dict:
            return {
                'row_count': len(chunk),
                'null_counts': chunk.isnull().sum().to_dict(),
                'numeric_stats': chunk.select_dtypes(include=['number']).describe().to_dict() 
                                 if len(chunk.select_dtypes(include=['number']).columns) > 0 else {},
                'columns': list(chunk.columns),
                'dtypes': {col: str(dtype) for col, dtype in chunk.dtypes.items()},
            }
        
        def aggregate_stats(results: list[dict]) -> dict:
            if not results:
                return {}
            
            total_rows = sum(r['row_count'] for r in results)
            
            # Aggregate null counts
            all_null_counts = {}
            for r in results:
                for col, count in r['null_counts'].items():
                    all_null_counts[col] = all_null_counts.get(col, 0) + count
            
            # Use first result for columns and dtypes
            first = results[0]
            
            return {
                'total_rows': total_rows,
                'total_chunks': len(results),
                'columns': first['columns'],
                'column_count': len(first['columns']),
                'dtypes': first['dtypes'],
                'null_counts': all_null_counts,
                'null_percentages': {
                    col: round(count / total_rows * 100, 2) if total_rows > 0 else 0
                    for col, count in all_null_counts.items()
                },
            }
        
        return self.process_chunked(file_path, process_chunk, aggregate_stats)
    
    def find_unique_keys_chunked(self, file_path: Path, 
                                  key_columns: list[str]) -> set:
        """
        Find all unique key combinations in a large file.
        """
        all_keys = set()
        
        for chunk in self.read_csv_chunked(file_path):
            if not all(col in chunk.columns for col in key_columns):
                continue
            
            # Create composite keys
            keys = chunk[key_columns].astype(str).agg('|'.join, axis=1)
            all_keys.update(keys.tolist())
        
        return all_keys
    
    def compare_large_files_chunked(self, 
                                    file1_path: Path,
                                    file2_path: Path,
                                    key_columns: list[str]) -> dict:
        """
        Compare two large files using chunked processing.
        Returns set-based comparison without loading full files.
        
        Uses Rust acceleration when available for 10x-50x faster set operations.
        """
        logger.info(f"Starting chunked comparison of {file1_path.name} and {file2_path.name}")
        
        # Get unique keys from both files
        keys1 = self.find_unique_keys_chunked(file1_path, key_columns)
        keys2 = self.find_unique_keys_chunked(file2_path, key_columns)
        
        # Use Rust for set operations if available
        if self._use_rust:
            result = self._compare_sets_rust(
                file1_path.name, keys1, 
                file2_path.name, keys2
            )
        else:
            result = self._compare_sets_python(
                file1_path.name, keys1, 
                file2_path.name, keys2
            )
        
        result['rust_accelerated'] = self._use_rust
        return result
    
    def _compare_sets_rust(self, 
                           file1_name: str, keys1: set,
                           file2_name: str, keys2: set) -> dict:
        """
        Use Rust FastIntersector for high-performance set comparison.
        """
        logger.debug("Using Rust-accelerated set comparison")
        
        intersector = FastIntersector()
        intersector.add_file(file1_name, list(keys1))
        intersector.add_file(file2_name, list(keys2))
        
        rust_result = intersector.compute()
        
        # Extract results from Rust
        file_exclusive = dict(rust_result.file_exclusive_counts)
        overlap_count = rust_result.overlap_count
        total_unique = rust_result.total_unique_keys
        
        # Calculate samples for exclusive keys
        only_in_1 = keys1 - keys2
        only_in_2 = keys2 - keys1
        
        return {
            'file1_keys': len(keys1),
            'file2_keys': len(keys2),
            'common_keys': overlap_count,
            'only_in_file1': file_exclusive.get(file1_name, len(only_in_1)),
            'only_in_file2': file_exclusive.get(file2_name, len(only_in_2)),
            'only_in_file1_sample': list(only_in_1)[:10],
            'only_in_file2_sample': list(only_in_2)[:10],
            'overlap_percentage': round(overlap_count / total_unique * 100, 2) 
                                  if total_unique > 0 else 0,
        }
    
    def _compare_sets_python(self, 
                             file1_name: str, keys1: set,
                             file2_name: str, keys2: set) -> dict:
        """
        Pure Python fallback for set comparison.
        """
        logger.debug("Using Python fallback for set comparison")
        
        # Set operations
        common_keys = keys1 & keys2
        only_in_1 = keys1 - keys2
        only_in_2 = keys2 - keys1
        
        return {
            'file1_keys': len(keys1),
            'file2_keys': len(keys2),
            'common_keys': len(common_keys),
            'only_in_file1': len(only_in_1),
            'only_in_file2': len(only_in_2),
            'only_in_file1_sample': list(only_in_1)[:10],
            'only_in_file2_sample': list(only_in_2)[:10],
            'overlap_percentage': round(len(common_keys) / len(keys1 | keys2) * 100, 2) 
                                  if keys1 | keys2 else 0,
        }
    
    def compare_multiple_files_chunked(self,
                                        file_paths: list[Path],
                                        key_columns: list[str]) -> dict:
        """
        Compare multiple large files using chunked processing and Rust acceleration.
        
        This is ideal for comparing 3+ large files without loading them into memory.
        
        Args:
            file_paths: List of paths to CSV files
            key_columns: Columns to use for key generation
            
        Returns:
            Comprehensive comparison results
        """
        logger.info(f"Starting multi-file chunked comparison of {len(file_paths)} files")
        
        # Extract keys from all files
        file_keys = {}
        for path in file_paths:
            keys = self.find_unique_keys_chunked(path, key_columns)
            file_keys[path.name] = keys
            logger.debug(f"Extracted {len(keys)} keys from {path.name}")
        
        if self._use_rust:
            return self._compare_multiple_rust(file_keys)
        else:
            return self._compare_multiple_python(file_keys)
    
    def _compare_multiple_rust(self, file_keys: dict[str, set]) -> dict:
        """
        Use Rust FastIntersector for multi-file comparison.
        """
        logger.debug("Using Rust-accelerated multi-file comparison")
        
        intersector = FastIntersector()
        
        for filename, keys in file_keys.items():
            intersector.add_file(filename, list(keys))
        
        rust_result = intersector.compute()
        
        return {
            'file_count': len(file_keys),
            'file_names': list(file_keys.keys()),
            'total_unique_keys': rust_result.total_unique_keys,
            'keys_in_all_files': rust_result.overlap_count,
            'file_exclusive_counts': dict(rust_result.file_exclusive_counts),
            'rust_accelerated': True,
        }
    
    def _compare_multiple_python(self, file_keys: dict[str, set]) -> dict:
        """
        Pure Python fallback for multi-file comparison.
        """
        logger.debug("Using Python fallback for multi-file comparison")
        
        all_keys = set()
        for keys in file_keys.values():
            all_keys.update(keys)
        
        # Find keys in all files
        keys_in_all = all_keys.copy()
        for keys in file_keys.values():
            keys_in_all &= keys
        
        # Count file-exclusive keys
        file_exclusive_counts = {}
        for filename, keys in file_keys.items():
            other_keys = set()
            for other_name, other in file_keys.items():
                if other_name != filename:
                    other_keys.update(other)
            exclusive = keys - other_keys
            file_exclusive_counts[filename] = len(exclusive)
        
        return {
            'file_count': len(file_keys),
            'file_names': list(file_keys.keys()),
            'total_unique_keys': len(all_keys),
            'keys_in_all_files': len(keys_in_all),
            'file_exclusive_counts': file_exclusive_counts,
            'rust_accelerated': False,
        }
    
    def sample_large_file(self, file_path: Path, 
                          sample_size: int = 1000,
                          method: str = 'random') -> pd.DataFrame:
        """
        Get a sample from a large file without loading the entire file.
        
        Args:
            file_path: Path to file
            sample_size: Number of rows to sample
            method: 'random', 'head', 'tail', or 'stratified'
            
        Returns:
            Sampled DataFrame
        """
        if method == 'head':
            return pd.read_csv(file_path, nrows=sample_size)
        
        elif method == 'tail':
            # Need to count rows first
            row_count = sum(1 for _ in self.read_csv_chunked(file_path))
            if row_count <= sample_size:
                return pd.read_csv(file_path)
            
            skip_rows = row_count - sample_size
            return pd.read_csv(file_path, skiprows=range(1, skip_rows + 1))
        
        elif method == 'random':
            # Reservoir sampling across chunks
            sample = []
            total_seen = 0
            
            for chunk in self.read_csv_chunked(file_path):
                chunk_size = len(chunk)
                
                if total_seen == 0:
                    # First chunk - take up to sample_size
                    sample = chunk.head(sample_size).to_dict('records')
                else:
                    # Reservoir sampling
                    for i, row in chunk.iterrows():
                        total_seen_before = total_seen
                        total_seen += 1
                        
                        if len(sample) < sample_size:
                            sample.append(row.to_dict())
                        else:
                            # Replace with decreasing probability
                            j = np.random.randint(0, total_seen)
                            if j < sample_size:
                                sample[j] = row.to_dict()
                
                total_seen += chunk_size
            
            return pd.DataFrame(sample)
        
        else:
            raise ValueError(f"Unknown sampling method: {method}")


class ParallelProcessor:
    """
    Parallel processing utilities for multiple files.
    """
    
    def __init__(self, max_workers: int = MAX_WORKERS):
        self.max_workers = max_workers
    
    def process_files_parallel(self, 
                               file_paths: list[Path],
                               processor: Callable[[Path], dict]) -> dict[str, dict]:
        """
        Process multiple files in parallel.
        
        Args:
            file_paths: List of file paths
            processor: Function to process each file
            
        Returns:
            Dict mapping filename to result
        """
        results = {}
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_file = {
                executor.submit(processor, path): path 
                for path in file_paths
            }
            
            for future in as_completed(future_to_file):
                file_path = future_to_file[future]
                try:
                    result = future.result()
                    results[file_path.name] = result
                except Exception as e:
                    logger.error(f"Error processing {file_path.name}: {str(e)}")
                    results[file_path.name] = {"error": str(e)}
        
        return results
    
    def load_dataframes_parallel(self, 
                                 file_paths: list[Path],
                                 loader: Callable[[Path], pd.DataFrame]) -> dict[str, pd.DataFrame]:
        """
        Load multiple dataframes in parallel.
        """
        results = {}
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_file = {
                executor.submit(loader, path): path 
                for path in file_paths
            }
            
            for future in as_completed(future_to_file):
                file_path = future_to_file[future]
                try:
                    df = future.result()
                    results[file_path.name] = df
                except Exception as e:
                    logger.error(f"Error loading {file_path.name}: {str(e)}")
        
        return results
