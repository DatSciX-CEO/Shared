use pyo3::prelude::*;
use std::collections::{HashMap, HashSet};
use ahash::RandomState;
use rayon::prelude::*;

/// Result structure for multi-file intersection
#[pyclass]
#[derive(Clone)]
pub struct IntersectionResult {
    #[pyo3(get)]
    pub presence_matrix: Vec<Vec<bool>>,
    #[pyo3(get)]
    pub keys: Vec<String>,
    #[pyo3(get)]
    pub file_exclusive_counts: HashMap<String, usize>,
    #[pyo3(get)]
    pub overlap_count: usize,
    #[pyo3(get)]
    pub total_unique_keys: usize,
}

/// A fast engine for calculating intersections across multiple datasets.
#[pyclass]
pub struct FastIntersector {
    file_map: HashMap<String, HashSet<String, RandomState>>,
}

#[pymethods]
impl FastIntersector {
    #[new]
    pub fn new() -> Self {
        FastIntersector {
            file_map: HashMap::new(),
        }
    }

    /// Add a file's keys to the intersector.
    /// Keys are expected to be the "composite keys" (e.g. "val1|val2").
    pub fn add_file(&mut self, filename: String, keys: Vec<String>) {
        let set: HashSet<String, RandomState> = keys.into_iter().collect();
        self.file_map.insert(filename, set);
    }

    /// Compute the intersection matrix and statistics.
    pub fn compute(&self) -> IntersectionResult {
        // 1. Collect all unique keys across all files (Union)
        let all_keys: HashSet<&String, RandomState> = self.file_map.values()
            .flat_map(|set| set.iter())
            .collect();
        
        let mut sorted_keys: Vec<String> = all_keys.into_iter().cloned().collect();
        // Sorting keys ensures deterministic output for the matrix
        sorted_keys.par_sort();

        let filenames: Vec<String> = self.file_map.keys().cloned().collect();
        let total_unique_keys = sorted_keys.len();
        
        // 2. Build Presence Matrix (Parallelized)
        // Rows: Keys, Cols: Files. true = key exists in file.
        let presence_matrix: Vec<Vec<bool>> = sorted_keys.par_iter()
            .map(|key| {
                filenames.iter()
                    .map(|fname| self.file_map.get(fname).unwrap().contains(key))
                    .collect()
            })
            .collect();

        // 3. Calculate Statistics
        let mut file_exclusive_counts: HashMap<String, usize> = HashMap::new();
        for fname in &filenames {
            file_exclusive_counts.insert(fname.clone(), 0);
        }

        let mut overlap_count = 0;

        for row in &presence_matrix {
            let present_in_count = row.iter().filter(|&&present| present).count();
            
            if present_in_count == filenames.len() {
                overlap_count += 1;
            } else if present_in_count == 1 {
                // Find which file it is exclusive to
                for (idx, &present) in row.iter().enumerate() {
                    if present {
                        let fname = &filenames[idx];
                        *file_exclusive_counts.get_mut(fname).unwrap() += 1;
                        break;
                    }
                }
            }
        }

        IntersectionResult {
            presence_matrix,
            keys: sorted_keys,
            file_exclusive_counts,
            overlap_count,
            total_unique_keys,
        }
    }
    
    /// Get the list of files currently tracked
    pub fn get_filenames(&self) -> Vec<String> {
        self.file_map.keys().cloned().collect()
    }
    
    /// Clear all files from the intersector
    pub fn clear(&mut self) {
        self.file_map.clear();
    }
    
    /// Get count of files currently tracked
    pub fn file_count(&self) -> usize {
        self.file_map.len()
    }
}

/// A Python module implemented in Rust.
#[pymodule]
fn viewerit_core(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<FastIntersector>()?;
    m.add_class::<IntersectionResult>()?;
    Ok(())
}
