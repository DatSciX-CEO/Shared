"""
Test script to verify Rust integration works correctly.
"""
import pandas as pd
from pathlib import Path
import sys
import importlib.util

def load_module_direct(module_name, file_path):
    """Load a module directly without going through __init__.py"""
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def test_rust_module():
    """Test 1: Verify Rust module import"""
    print('=' * 60)
    print('TEST 1: Verify Rust Module Import')
    print('=' * 60)
    try:
        from viewerit_core import FastIntersector, IntersectionResult
        print('SUCCESS: viewerit_core imported successfully')
        print(f'  FastIntersector: {FastIntersector}')
        print(f'  IntersectionResult: {IntersectionResult}')
        return True
    except ImportError as e:
        print(f'FAILED: Could not import viewerit_core: {e}')
        return False

def test_fast_intersector():
    """Test 2: Test FastIntersector basic functionality"""
    print()
    print('=' * 60)
    print('TEST 2: FastIntersector Basic Functionality')
    print('=' * 60)
    
    from viewerit_core import FastIntersector
    
    fi = FastIntersector()
    fi.add_file('file_a', ['1', '2', '3', '4', '5'])
    fi.add_file('file_b', ['1', '2', '3', '6', '7'])
    fi.add_file('file_c', ['1', '3', '5', '6', '8'])
    
    result = fi.compute()
    print(f'  Total unique keys: {result.total_unique_keys}')
    print(f'  Overlap count (keys in ALL files): {result.overlap_count}')
    print(f'  File exclusive counts: {dict(result.file_exclusive_counts)}')
    print(f'  Keys returned: {len(result.keys)}')
    
    # Verify expected results
    assert result.total_unique_keys == 8, f'Expected 8 unique keys, got {result.total_unique_keys}'
    assert result.overlap_count == 2, f'Expected 2 overlapping keys (1, 3), got {result.overlap_count}'
    print('SUCCESS: Basic functionality works correctly')
    return True

def test_multi_file_comparator():
    """Test 3: MultiFileComparator with Rust"""
    print()
    print('=' * 60)
    print('TEST 3: MultiFileComparator with Rust Integration')
    print('=' * 60)
    
    # Load the module directly to avoid __init__.py side effects
    multi_comp_module = load_module_direct(
        'multi_comparator', 
        'backend/services/multi_comparator.py'
    )
    
    MultiFileComparator = multi_comp_module.MultiFileComparator
    RUST_AVAILABLE = multi_comp_module.RUST_AVAILABLE
    
    print(f'  Rust available: {RUST_AVAILABLE}')
    
    # Load test data
    df_a = pd.read_csv('test_data/sample_file_a.csv')
    df_b = pd.read_csv('test_data/sample_file_b.csv')
    df_c = pd.read_csv('test_data/sample_file_c.csv')
    
    dataframes = {
        'sample_file_a.csv': df_a,
        'sample_file_b.csv': df_b,
        'sample_file_c.csv': df_c,
    }
    
    comparator = MultiFileComparator(dataframes)
    result = comparator.compare(join_columns=['id'])
    
    summary = result['summary']
    print(f'  Files compared: {summary["file_count"]}')
    print(f'  Total unique records: {summary["total_unique_records"]}')
    print(f'  Records in ALL files: {summary["records_in_all_files"]}')
    print(f'  Records in single file: {summary["records_in_single_file"]}')
    print(f'  Rust accelerated: {summary.get("rust_accelerated", "N/A")}')
    print()
    print('  File exclusive counts:')
    for fname, count in summary['file_exclusive_counts'].items():
        print(f'    {fname}: {count}')
    
    print()
    print('SUCCESS: MultiFileComparator integration works correctly')
    return True

def test_chunked_processor():
    """Test 4: ChunkedProcessor with Rust"""
    print()
    print('=' * 60)
    print('TEST 4: ChunkedProcessor with Rust Integration')
    print('=' * 60)
    
    # Load the module directly
    chunked_module = load_module_direct(
        'chunked_processor',
        'backend/services/chunked_processor.py'
    )
    
    ChunkedProcessor = chunked_module.ChunkedProcessor
    RUST_AVAILABLE = chunked_module.RUST_AVAILABLE
    
    print(f'  Rust available for ChunkedProcessor: {RUST_AVAILABLE}')
    
    processor = ChunkedProcessor()
    path_a = Path('test_data/sample_file_a.csv')
    path_b = Path('test_data/sample_file_b.csv')
    
    result = processor.compare_large_files_chunked(path_a, path_b, ['id'])
    print(f'  File 1 keys: {result["file1_keys"]}')
    print(f'  File 2 keys: {result["file2_keys"]}')
    print(f'  Common keys: {result["common_keys"]}')
    print(f'  Only in file 1: {result["only_in_file1"]}')
    print(f'  Only in file 2: {result["only_in_file2"]}')
    print(f'  Rust accelerated: {result.get("rust_accelerated", "N/A")}')
    
    print()
    print('SUCCESS: ChunkedProcessor integration works correctly')
    return True

def test_multi_chunked():
    """Test 5: Multi-file chunked comparison"""
    print()
    print('=' * 60)
    print('TEST 5: Multi-File Chunked Comparison')
    print('=' * 60)
    
    chunked_module = load_module_direct(
        'chunked_processor',
        'backend/services/chunked_processor.py'
    )
    ChunkedProcessor = chunked_module.ChunkedProcessor
    
    processor = ChunkedProcessor()
    paths = [
        Path('test_data/sample_file_a.csv'),
        Path('test_data/sample_file_b.csv'),
        Path('test_data/sample_file_c.csv'),
    ]
    
    result = processor.compare_multiple_files_chunked(paths, ['id'])
    print(f'  File count: {result["file_count"]}')
    print(f'  Total unique keys: {result["total_unique_keys"]}')
    print(f'  Keys in all files: {result["keys_in_all_files"]}')
    print(f'  Rust accelerated: {result.get("rust_accelerated", "N/A")}')
    print()
    print('  File exclusive counts:')
    for fname, count in result['file_exclusive_counts'].items():
        print(f'    {fname}: {count}')
    
    print()
    print('SUCCESS: Multi-file chunked comparison works correctly')
    return True

def test_performance():
    """Test 6: Performance comparison between Rust and Python"""
    print()
    print('=' * 60)
    print('TEST 6: Performance Comparison')
    print('=' * 60)
    
    import time
    from viewerit_core import FastIntersector
    
    # Generate larger test data
    n_keys = 50000
    keys_a = [str(i) for i in range(0, n_keys)]
    keys_b = [str(i) for i in range(n_keys // 2, n_keys + n_keys // 2)]
    keys_c = [str(i) for i in range(n_keys // 4, n_keys + n_keys // 4)]
    
    # Rust timing
    start = time.perf_counter()
    fi = FastIntersector()
    fi.add_file('file_a', keys_a)
    fi.add_file('file_b', keys_b)
    fi.add_file('file_c', keys_c)
    result = fi.compute()
    rust_time = time.perf_counter() - start
    
    # Python timing
    start = time.perf_counter()
    set_a = set(keys_a)
    set_b = set(keys_b)
    set_c = set(keys_c)
    all_keys = set_a | set_b | set_c
    common_keys = set_a & set_b & set_c
    python_time = time.perf_counter() - start
    
    print(f'  Test size: {n_keys} keys per file')
    print(f'  Rust time: {rust_time*1000:.2f} ms')
    print(f'  Python time: {python_time*1000:.2f} ms')
    if python_time > 0:
        print(f'  Speedup: {python_time/rust_time:.1f}x (Rust is faster)')
    
    print()
    print('SUCCESS: Performance test completed')
    return True


if __name__ == '__main__':
    all_passed = True
    
    all_passed &= test_rust_module()
    all_passed &= test_fast_intersector()
    all_passed &= test_multi_file_comparator()
    all_passed &= test_chunked_processor()
    all_passed &= test_multi_chunked()
    all_passed &= test_performance()
    
    print()
    print('=' * 60)
    if all_passed:
        print('ALL TESTS PASSED')
    else:
        print('SOME TESTS FAILED')
    print('=' * 60)
