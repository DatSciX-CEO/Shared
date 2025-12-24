/**
 * API Hook - Handles all backend communication
 */
import { useState, useCallback } from 'react';
import axios, { AxiosError } from 'axios';

const API_BASE = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Types
export interface FileInfo {
  filename: string;
  session_id: string;
  file_size: number;
  rows: number;
  columns: number;
  column_names: string[];
  dtypes: Record<string, string>;
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
}

export interface OllamaModel {
  name: string;
  size: number;
  family: string;
  error?: string;
}

export interface AIResponse {
  success: boolean;
  response?: string;
  error?: string;
  model: string;
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
  const uploadFiles = useCallback(async (files: File[]): Promise<{ session_id: string; files: string[] } | null> => {
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

  // Comparison Operations
  const compareFiles = useCallback(async (
    sessionId: string,
    file1: string,
    file2: string,
    joinColumns: string[],
    ignoreColumns?: string[]
  ): Promise<ComparisonResult | null> => {
    setLoading(true);
    setError(null);
    try {
      const response = await api.post('/compare', {
        session_id: sessionId,
        file1,
        file2,
        join_columns: joinColumns,
        ignore_columns: ignoreColumns,
      });
      return response.data;
    } catch (err) {
      handleError(err);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  // AI Operations
  const getModels = useCallback(async (): Promise<OllamaModel[]> => {
    try {
      const response = await api.get('/ai/models');
      return response.data.models;
    } catch (err) {
      handleError(err);
      return [];
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

  return {
    loading,
    error,
    setError,
    uploadFiles,
    getFileInfo,
    getFilePreview,
    compareFiles,
    getModels,
    analyzeWithAI,
    suggestJoinColumns,
  };
}

export default useApi;

