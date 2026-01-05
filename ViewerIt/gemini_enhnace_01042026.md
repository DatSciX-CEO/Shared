# ViewerIt: Rust Enhancement Plan & Architecture Analysis

**Date:** January 4, 2026
**Target:** Performance, Safety, and Scalability
**Status:** Approved for Implementation

## 1. Architecture Analysis

### Current State (Python-Native)
The current backend relies heavily on `pandas` for data processing. While excellent for prototyping and small datasets, several bottlenecks exist in the current implementation, particularly for the "Multi-File Comparison" and "Schema Analysis" features:

*   **Memory Overhead:** `MultiFileComparator` loads all dataframes into memory simultaneously. Python objects (especially strings in pandas) have significant overhead.
*   **Iteration Performance:** Logic that involves iterating over rows (e.g., building the "presence matrix" or reconciling records) is performed in Python loops, which are inherently slow due to the GIL and interpretation overhead.
*   **Type Safety:** File ingestion relies on runtime checks. Malformed CSVs or ambiguous encodings are often detected late in the pipeline.

### The Solution: "Rust Core, Python Shell"
We will not rewrite the entire application. Instead, we will inject **Rust** into specific "hot paths" where performance matches the complexity cost. We will use `PyO3` to create a native Python extension module that allows existing Python code to call Rust functions as if they were standard library calls.

---

## 2. Implementation Plan

### Phase 1: Infrastructure & Scaffolding (Immediate)
**Goal:** Establish the build pipeline for mixed Python/Rust development.

*   **Tooling:** Use `maturin` as the build backend to compile Rust crates into Python wheels.
*   **Structure:** Create `backend/rust_core` to house the Rust source.
*   **Integration:** seamless import in Python (e.g., `from viewerit_core import fast_intersect`).

### Phase 2: The "FastIntersector" Engine (High Impact)
**Goal:** Optimize the O(N) multi-file intersection logic.

*   **Problem:** Currently, `MultiFileComparator` builds massive dictionaries to map keys to files.
*   **Rust Solution:**
    *   **Input:** Receive list of "Composite Keys" (strings) from Python.
    *   **Logic:** Use Rust's `HashSet` and `DashMap` (for parallelism) to compute intersections.
    *   **Output:** Return the "Presence Matrix" and Venn diagram data structure directly.
    *   **Benefit:** Estimated **10x-50x speedup** for set operations; drastic memory reduction.

### Phase 3: Streaming CSV Processor (Scalability)
**Goal:** Handle multi-gigabyte files without crashing RAM.

*   **Problem:** `pandas.read_csv` (even chunked) allocates memory for the chunk before processing.
*   **Rust Solution:**
    *   Use the `csv` crate for zero-copy parsing.
    *   Implement a "Scanner" that calculates row counts, null distribution, and type inference by reading the byte stream directly.
    *   **Benefit:** Instant file previews and stats for huge files.

### Phase 4: Safety & Validation
*   **Strict Parser:** A Rust-based schema validator that enforces column types at the byte level before Python ever touches the data.

---

## 3. Technical Roadmap

### Directory Structure
```text
C:\Shared\ViewerIt\
├── backend\
│   ├── rust_core\          <-- NEW: Rust source code
│   │   ├── src\
│   │   │   └── lib.rs      <-- PyO3 module definition
│   │   ├── Cargo.toml      <-- Dependencies (serde, rayon, pyo3)
│   │   └── pyproject.toml  <-- Build config
│   ├── services\
│   │   └── multi_comparator.py  <-- Update to use rust_core
```

### Key Dependencies
*   **`pyo3`**: The bridge between Python and Rust.
*   **`maturin`**: Build system.
*   **`rayon`**: Data parallelism (multi-threading).
*   **`ahash`**: Faster hashing algorithm for set operations.

---

## 4. Execution Steps (Next Actions)

1.  **Scaffold:** Initialize the `rust_core` crate.
2.  **Develop:** Implement `FastIntersector` in Rust.
3.  **Bind:** Expose the struct to Python via PyO3.
4.  **Integrate:** Update `MultiFileComparator` to offload set logic to Rust.
