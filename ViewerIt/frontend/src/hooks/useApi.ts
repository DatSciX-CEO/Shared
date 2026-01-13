/**
 * API Hook - Handles all backend communication
 * Enhanced with multi-file comparison, schema analysis, and quality checking
 */
import { useState, useCallback } from 'react';
import axios, { AxiosError } from 'axios';

const API_BASE = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 300000, // 5 minute timeout for large operations
});

// Types
export interface FileInfo {
  filename: string;
  session_id: string;
  file_size: number;
  file_size_mb?: number;
  rows: number;
  columns: number;
  column_names: string[];
  dtypes: Record<string, string>;
  format?: string;
  memory_usage_mb?: number;
  null_counts?: Record<string, number>;
}

export interface ComparisonResult {
  matches: boolean;
  summary: {
    df1_name: string;
    df2_name: string;
    df1_rows: number;
    df2_rows: number;
    df1_columns: number;
    df2_columns: number;
    common_rows: number;
    common_columns: number;
  };
  columns: {
    only_in_df1: string[];
    only_in_df2: string[];
    common: string[];
    mismatched: string[];
  };
  rows: {
    only_in_df1_count: number;
    only_in_df2_count: number;
    only_in_df1_sample: Record<string, unknown>[];
    only_in_df2_sample: Record<string, unknown>[];
  };
  column_stats: Array<{
    column: string;
    mismatch_count: number;
  }>;
  text_report: string;
  statistics?: Record<string, unknown>;
  file1?: string;
  file2?: string;
}

export interface MultiComparisonResult {
  comparisons: ComparisonResult[];
}

export interface MultiFileComparisonResult {
  summary: {
    total_unique_records: number;
    file_count: number;
    file_names: string[];
    records_in_all_files: number;
    records_in_multiple_files: number;
    records_in_single_file: number;
    file_record_counts: Record<string, number>;
    file_exclusive_counts: Record<string, number>;
    overlap_percentage: number;
  };
  records_in_all_files: {
    count: number;
    samples: Array<Record<string, unknown>>;
  };
  records_in_some_files: {
    count: number;
    by_file_count: Record<string, { count: number; samples: Array<Record<string, unknown>> }>;
    samples: Array<Record<string, unknown>>;
  };
  records_in_one_file: {
    count: number;
    by_file: Record<string, number>;
    samples: Array<Record<string, unknown>>;
  };
  presence_matrix: {
    headers: string[];
    rows: Array<unknown[]>;
  };
  value_differences: Record<string, {
    mismatch_count: number;
    samples: Array<{ key: string; values: Record<string, unknown> }>;
  }>;
  column_analysis: {
    all_columns: string[];
    columns_in_all_files: string[];
    columns_in_some_files: Record<string, string[]>;
    file_unique_columns: Record<string, string[]>;
    column_types: Record<string, Record<string, string>>;
    type_mismatches: Record<string, Record<string, string>>;
  };
  venn_data: {
    file_names: string[];
    sets: Array<{ sets: string[]; size: number }>;
  };
  reconciliation_report?: {
    summary: Record<string, unknown>;
    recommendations: Array<{ type: string; message: string; action?: string }>;
    action_items: unknown[];
  };
  warnings?: Array<{
    type: string;
    files?: string[];
    message: string;
    suggestion?: string;
  }>;
}

export interface ChunkedComparisonResult {
  file1: string;
  file2: string;
  file1_keys: number;
  file2_keys: number;
  common_keys: number;
  only_in_file1: number;
  only_in_file2: number;
  only_in_file1_sample: string[];
  only_in_file2_sample: string[];
  overlap_percentage: number;
  method: 'chunked';
  memory_efficient: boolean;
}

export interface ChunkedFileStats {
  filename: string;
  total_rows: number;
  total_chunks: number;
  columns: string[];
  column_count: number;
  dtypes: Record<string, string>;
  null_counts: Record<string, number>;
  null_percentages: Record<string, number>;
  method: 'chunked';
}

export interface SchemaAnalysisResult {
  schemas: Record<string, {
    columns: Record<string, {
      dtype: string;
      nullable: boolean;
      null_count: number;
      null_percentage: number;
      unique_count: number;
      unique_percentage: number;
      min?: number;
      max?: number;
      mean?: number;
      avg_length?: number;
      max_length?: number;
      sample_values?: unknown[];
    }>;
    row_count: number;
    column_count: number;
    memory_usage: number;
  }>;
  column_alignment: {
    all_columns: string[];
    columns_in_all_files: string[];
    columns_in_some_files: Record<string, string[]>;
    file_unique_columns: Record<string, string[]>;
    column_presence_matrix: Record<string, Record<string, boolean>>;
  };
  type_compatibility: {
    column_types: Record<string, {
      types: Record<string, string>;
      unique_types: string[];
      is_compatible: boolean;
      compatibility_group: string;
    }>;
    compatible_columns: string[];
    incompatible_columns: string[];
    compatibility_matrix: {
      columns: string[];
      files: string[];
      data: Array<Record<string, unknown>>;
    };
  };
  mapping_suggestions: {
    suggestions: Array<{
      file1: string;
      column1: string;
      file2: string;
      column2: string;
      similarity_score: number;
      match_reasons: string[];
    }>;
    total_suggestions: number;
  };
  issues: Array<{
    type: string;
    severity: string;
    column?: string;
    file?: string;
    message: string;
    details?: Record<string, unknown>;
  }>;
  summary: {
    file_count: number;
    total_unique_columns: number;
    columns_in_all_files: number;
    columns_in_some_files: number;
    schema_compatibility: string;
    issue_count: { high: number; medium: number; total: number };
    file_details: Record<string, { columns: number; rows: number }>;
  };
}

export interface QualityCheckResult {
  dataset_name: string;
  row_count: number;
  column_count: number;
  quality_score: {
    total: number;
    grade: string;
    breakdown: {
      completeness: number;
      uniqueness: number;
      validity: number;
      consistency: number;
      outliers: number;
    };
  };
  completeness: {
    total_cells: number;
    total_nulls: number;
    overall_completeness: number;
    column_completeness: Record<string, {
      null_count: number;
      null_percentage: number;
      complete_count: number;
      is_complete: boolean;
    }>;
    empty_columns: string[];
    high_null_columns: string[];
    complete_columns: string[];
  };
  uniqueness: {
    duplicate_row_count: number;
    duplicate_row_percentage: number;
    duplicate_row_indices_sample: number[];
    column_uniqueness: Record<string, {
      unique_count: number;
      unique_percentage: number;
      duplicate_count: number;
      is_unique: boolean;
      cardinality: string;
    }>;
    potential_id_columns: string[];
    categorical_columns: string[];
  };
  validity: Record<string, {
    dtype: string;
    format_checks: Record<string, {
      match_count: number;
      match_percentage: number;
      non_matching_samples: string[];
    }>;
    issues: Array<{ type: string; count?: number; message: string }>;
    case_consistency?: { consistent: boolean; pattern: string; distribution?: Record<string, number> };
  }>;
  consistency: {
    checks_performed: number;
    issues: Array<{ type: string; columns?: string[]; correlation?: number; message: string }>;
  };
  outliers: {
    columns_checked: number;
    columns_with_outliers: number;
    column_outliers: Record<string, {
      method: string;
      outlier_count: number;
      outlier_percentage: number;
      lower_bound: number;
      upper_bound: number;
      outlier_values_sample: number[];
      statistics: { mean: number; std: number; min: number; max: number; Q1: number; Q3: number };
    }>;
  };
  summary: Record<string, unknown>;
  recommendations: Array<{
    category: string;
    priority: string;
    message: string;
    columns?: string[];
    column?: string;
    action?: string;
  }>;
}

export interface MultiQualityResult {
  individual_results: Record<string, QualityCheckResult>;
  comparison: {
    scores: Record<string, number>;
    best_quality: string;
    completeness_comparison: Record<string, number>;
    duplicate_comparison: Record<string, number>;
  };
  overall_summary: {
    dataset_count: number;
    total_rows: number;
    average_quality_score: number;
    average_grade: string;
  };
}

export interface OllamaModel {
  name: string;
  size: number;
  size_human: string;
  family: string;
  parameter_size: string;
  quantization: string;
  format: string;
  families: string[];
  is_available: boolean;
  modified_at?: string;
  error?: string;
}

export interface OllamaStatus {
  online: boolean;
  count: number;
  recommended: string | null;
  error?: string;
  setup_hint?: string;
}

export interface OllamaModelsResponse {
  models: OllamaModel[];
  status: OllamaStatus;
}

export interface AIResponse {
  success: boolean;
  response?: string;
  error?: string;
  model: string;
}

// Task types for async operations
export interface TaskInfo {
  id: string;
  task_type: string;
  status: 'pending' | 'in_progress' | 'completed' | 'failed';
  progress: number;
  message: string;
  error: string | null;
  created_at: string;
  updated_at: string;
  completed_at: string | null;
  has_result: boolean;
}

export interface TaskResponse<T = unknown> {
  task_id: string;
  status: string;
  message: string;
  poll_url: string;
  result?: T;
  warnings?: Array<{
    type: string;
    files?: string[];
    message: string;
    suggestion?: string;
  }>;
}

export interface TaskStatusResponse<T = unknown> extends TaskInfo {
  result?: T;
}

// Custom hook for API operations
export function useApi() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleError = (err: unknown) => {
    if (err instanceof AxiosError) {
      setError(err.response?.data?.detail || err.message);
    } else if (err instanceof Error) {
      setError(err.message);
    } else {
      setError('An unknown error occurred');
    }
  };

  // File Operations
  const uploadFiles = useCallback(async (files: File[]): Promise<{ session_id: string; files: string[]; errors?: Array<{ file: string; error: string }> } | null> => {
    setLoading(true);
    setError(null);
    try {
      const formData = new FormData();
      files.forEach(file => formData.append('files', file));
      
      const response = await api.post('/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      return response.data;
    } catch (err) {
      handleError(err);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  const getFileInfo = useCallback(async (sessionId: string, filename: string): Promise<FileInfo | null> => {
    setLoading(true);
    setError(null);
    try {
      const response = await api.get(`/files/${sessionId}/${filename}/info`);
      return response.data;
    } catch (err) {
      handleError(err);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  const getFilePreview = useCallback(async (sessionId: string, filename: string, rows = 100): Promise<{
    columns: string[];
    data: Record<string, unknown>[];
    total_rows: number;
  } | null> => {
    setLoading(true);
    setError(null);
    try {
      const response = await api.get(`/files/${sessionId}/${filename}/preview`, {
        params: { rows },
      });
      return response.data;
    } catch (err) {
      handleError(err);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  const getExcelSheets = useCallback(async (sessionId: string, filename: string): Promise<string[]> => {
    try {
      const response = await api.get(`/files/${sessionId}/${filename}/sheets`);
      return response.data.sheets || [];
    } catch (err) {
      return [];
    }
  }, []);

  // Pairwise Comparison Operations
  // Uses /compare/sync for immediate results (suitable for smaller files)
  const compareFiles = useCallback(async (
    sessionId: string,
    files: string[],
    joinColumns: string[],
    ignoreColumns?: string[],
    options?: {
      absTol?: number;  // Absolute tolerance for numeric comparison
      relTol?: number;  // Relative tolerance for numeric comparison
    }
  ): Promise<MultiComparisonResult | null> => {
    setLoading(true);
    setError(null);
    try {
      // Use sync endpoint for immediate results
      const response = await api.post('/compare/sync', {
        session_id: sessionId,
        files,
        join_columns: joinColumns,
        ignore_columns: ignoreColumns,
        abs_tol: options?.absTol ?? 0.0001,
        rel_tol: options?.relTol ?? 0,
      });
      return response.data;
    } catch (err) {
      handleError(err);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  // Multi-File Comparison Operations
  // Uses /compare/multi/sync for immediate results (suitable for smaller files)
  const compareMultipleFiles = useCallback(async (
    sessionId: string,
    files: string[],
    joinColumns: string[],
    ignoreColumns?: string[],
    useChunked = false
  ): Promise<MultiFileComparisonResult | null> => {
    setLoading(true);
    setError(null);
    try {
      // Use sync endpoint for immediate results
      const response = await api.post('/compare/multi/sync', {
        session_id: sessionId,
        files,
        join_columns: joinColumns,
        ignore_columns: ignoreColumns,
        use_chunked: useChunked,
      });
      return response.data;
    } catch (err) {
      handleError(err);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  // Chunked Comparison for Large Files
  const compareLargeFilesChunked = useCallback(async (
    sessionId: string,
    file1: string,
    file2: string,
    joinColumns: string[]
  ): Promise<ChunkedComparisonResult | null> => {
    setLoading(true);
    setError(null);
    try {
      const response = await api.post('/compare/chunked', null, {
        params: {
          session_id: sessionId,
          file1,
          file2,
          join_columns: joinColumns,
        },
      });
      return response.data;
    } catch (err) {
      handleError(err);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  const getChunkedFileStats = useCallback(async (
    sessionId: string,
    filename: string
  ): Promise<ChunkedFileStats | null> => {
    setLoading(true);
    setError(null);
    try {
      const response = await api.get(`/files/${sessionId}/${filename}/chunked-stats`);
      return response.data;
    } catch (err) {
      handleError(err);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  // Schema Analysis Operations
  const analyzeSchemas = useCallback(async (
    sessionId: string,
    files: string[]
  ): Promise<SchemaAnalysisResult | null> => {
    setLoading(true);
    setError(null);
    try {
      const response = await api.post('/schema/analyze', {
        session_id: sessionId,
        files,
      });
      return response.data;
    } catch (err) {
      handleError(err);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  // Quality Check Operations
  // Uses /quality/check/sync for immediate results
  const checkQuality = useCallback(async (
    sessionId: string,
    files: string[]
  ): Promise<QualityCheckResult | MultiQualityResult | null> => {
    setLoading(true);
    setError(null);
    try {
      // Use sync endpoint for immediate results
      const response = await api.post('/quality/check/sync', {
        session_id: sessionId,
        files,
      });
      return response.data;
    } catch (err) {
      handleError(err);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  const getSingleFileQuality = useCallback(async (
    sessionId: string,
    filename: string
  ): Promise<QualityCheckResult | null> => {
    setLoading(true);
    setError(null);
    try {
      const response = await api.get(`/quality/${sessionId}/${filename}`);
      return response.data;
    } catch (err) {
      handleError(err);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  // AI Operations
  const getModels = useCallback(async (): Promise<OllamaModelsResponse> => {
    try {
      const response = await api.get('/ai/models');
      return response.data;
    } catch (err) {
      handleError(err);
      return {
        models: [],
        status: {
          online: false,
          count: 0,
          recommended: null,
          error: 'Failed to connect to backend',
        },
      };
    }
  }, []);

  const checkAIStatus = useCallback(async (): Promise<{ online: boolean; model_count: number; message: string; setup_hint?: string }> => {
    try {
      const response = await api.get('/ai/status');
      return response.data;
    } catch (err) {
      return {
        online: false,
        model_count: 0,
        message: 'Cannot connect to backend',
      };
    }
  }, []);

  const analyzeWithAI = useCallback(async (
    model: string,
    prompt: string,
    comparisonSummary: Record<string, unknown>
  ): Promise<AIResponse | null> => {
    setLoading(true);
    setError(null);
    try {
      const response = await api.post('/ai/analyze', {
        model,
        prompt,
        comparison_summary: comparisonSummary,
      });
      return response.data;
    } catch (err) {
      handleError(err);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  const suggestJoinColumns = useCallback(async (
    model: string,
    df1Columns: string[],
    df2Columns: string[]
  ): Promise<{ success: boolean; suggested_columns?: string[]; reasoning?: string } | null> => {
    setLoading(true);
    setError(null);
    try {
      const response = await api.post('/ai/suggest-join', {
        model,
        df1_columns: df1Columns,
        df2_columns: df2Columns,
      });
      return response.data;
    } catch (err) {
      handleError(err);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  // Format Detection
  const detectFormat = useCallback(async (file: File): Promise<{
    extension: string;
    format: string;
    is_supported: boolean;
    detected_encoding?: string;
    encoding_confidence?: number;
    might_be?: string;
  } | null> => {
    try {
      const formData = new FormData();
      formData.append('file', file);
      const response = await api.post('/formats/detect', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      return response.data;
    } catch (err) {
      handleError(err);
      return null;
    }
  }, []);

  const getSupportedFormats = useCallback(async (): Promise<Record<string, { name: string; description: string; mime_types: string[] }>> => {
    try {
      const response = await api.get('/formats');
      return response.data.formats || {};
    } catch (err) {
      return {};
    }
  }, []);

  // ============== Task Polling Operations ==============

  const getTaskStatus = useCallback(async <T = unknown>(taskId: string): Promise<TaskStatusResponse<T> | null> => {
    try {
      const response = await api.get(`/tasks/${taskId}`);
      return response.data;
    } catch (err) {
      handleError(err);
      return null;
    }
  }, []);

  const getTaskResult = useCallback(async <T = unknown>(taskId: string): Promise<T | null> => {
    try {
      const response = await api.get(`/tasks/${taskId}/result`);
      if (response.status === 202) {
        // Task still processing
        return null;
      }
      return response.data;
    } catch (err) {
      handleError(err);
      return null;
    }
  }, []);

  /**
   * Poll a task until completion with progress callback
   */
  const pollTaskUntilComplete = useCallback(async <T = unknown>(
    taskId: string,
    onProgress?: (progress: number, message: string) => void,
    pollInterval = 500,
    maxAttempts = 600 // 5 minutes max
  ): Promise<T | null> => {
    let attempts = 0;
    
    while (attempts < maxAttempts) {
      const status = await getTaskStatus<T>(taskId);
      
      if (!status) {
        return null;
      }
      
      // Report progress
      if (onProgress) {
        onProgress(status.progress, status.message);
      }
      
      // Check completion states
      if (status.status === 'completed') {
        return status.result ?? null;
      }
      
      if (status.status === 'failed') {
        setError(status.error || 'Task failed');
        return null;
      }
      
      // Wait before next poll
      await new Promise(resolve => setTimeout(resolve, pollInterval));
      attempts++;
    }
    
    setError('Task polling timeout');
    return null;
  }, [getTaskStatus]);

  // ============== Async Comparison with Task Polling ==============

  const compareFilesAsync = useCallback(async (
    sessionId: string,
    files: string[],
    joinColumns: string[],
    ignoreColumns?: string[],
    options?: {
      absTol?: number;
      relTol?: number;
    },
    onProgress?: (progress: number, message: string) => void
  ): Promise<MultiComparisonResult | null> => {
    setLoading(true);
    setError(null);
    try {
      // Start the task
      const response = await api.post('/compare', {
        session_id: sessionId,
        files,
        join_columns: joinColumns,
        ignore_columns: ignoreColumns,
        abs_tol: options?.absTol ?? 0.0001,
        rel_tol: options?.relTol ?? 0,
      });
      
      const taskResponse = response.data as TaskResponse;
      
      // Poll for result
      const result = await pollTaskUntilComplete<MultiComparisonResult>(
        taskResponse.task_id,
        onProgress
      );
      
      return result;
    } catch (err) {
      handleError(err);
      return null;
    } finally {
      setLoading(false);
    }
  }, [pollTaskUntilComplete]);

  const compareMultipleFilesAsync = useCallback(async (
    sessionId: string,
    files: string[],
    joinColumns: string[],
    ignoreColumns?: string[],
    useChunked = false,
    onProgress?: (progress: number, message: string) => void
  ): Promise<MultiFileComparisonResult | null> => {
    setLoading(true);
    setError(null);
    try {
      // Start the task
      const response = await api.post('/compare/multi', {
        session_id: sessionId,
        files,
        join_columns: joinColumns,
        ignore_columns: ignoreColumns,
        use_chunked: useChunked,
      });
      
      const taskResponse = response.data as TaskResponse;
      
      // Poll for result
      const result = await pollTaskUntilComplete<MultiFileComparisonResult>(
        taskResponse.task_id,
        onProgress
      );
      
      return result;
    } catch (err) {
      handleError(err);
      return null;
    } finally {
      setLoading(false);
    }
  }, [pollTaskUntilComplete]);

  const checkQualityAsync = useCallback(async (
    sessionId: string,
    files: string[],
    onProgress?: (progress: number, message: string) => void
  ): Promise<QualityCheckResult | MultiQualityResult | null> => {
    setLoading(true);
    setError(null);
    try {
      // Start the task
      const response = await api.post('/quality/check', {
        session_id: sessionId,
        files,
      });
      
      const taskResponse = response.data as TaskResponse;
      
      // Poll for result
      const result = await pollTaskUntilComplete<QualityCheckResult | MultiQualityResult>(
        taskResponse.task_id,
        onProgress
      );
      
      return result;
    } catch (err) {
      handleError(err);
      return null;
    } finally {
      setLoading(false);
    }
  }, [pollTaskUntilComplete]);

  // ============== AI Streaming ==============

  /**
   * Stream AI analysis with SSE - returns an async generator
   */
  const streamAIAnalysis = useCallback(async function* (
    model: string,
    prompt: string,
    comparisonSummary: Record<string, unknown>
  ): AsyncGenerator<{ type: string; content?: string; error?: string }> {
    const response = await fetch(`${API_BASE}/ai/analyze/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        model,
        prompt,
        comparison_summary: comparisonSummary,
      }),
    });

    if (!response.ok) {
      yield { type: 'error', error: 'Failed to connect to AI service' };
      return;
    }

    const reader = response.body?.getReader();
    if (!reader) {
      yield { type: 'error', error: 'No response body' };
      return;
    }

    const decoder = new TextDecoder();
    let buffer = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');
      buffer = lines.pop() || '';

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          try {
            const data = JSON.parse(line.slice(6));
            yield data;
          } catch {
            // Skip invalid JSON
          }
        }
      }
    }
  }, []);

  return {
    loading,
    error,
    setError,
    // File operations
    uploadFiles,
    getFileInfo,
    getFilePreview,
    getExcelSheets,
    // Comparison operations (sync)
    compareFiles,
    compareMultipleFiles,
    // Comparison operations (async with progress)
    compareFilesAsync,
    compareMultipleFilesAsync,
    // Chunked/Large file operations
    compareLargeFilesChunked,
    getChunkedFileStats,
    // Schema analysis
    analyzeSchemas,
    analyzeSchema: analyzeSchemas, // Alias for compatibility
    // Quality checking (sync and async)
    checkQuality,
    checkQualityAsync,
    getSingleFileQuality,
    // Task operations
    getTaskStatus,
    getTaskResult,
    pollTaskUntilComplete,
    // AI operations
    getModels,
    checkAIStatus,
    analyzeWithAI,
    suggestJoinColumns,
    streamAIAnalysis,
    // Format operations
    detectFormat,
    getSupportedFormats,
  };
}

export default useApi;
