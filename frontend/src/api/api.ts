import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_URL,
});

export interface ApiError {
  message: string;
  status?: number;
  details?: unknown;
}

interface KeyClause {
  type: string;
  content: string;
  importance: 'high' | 'medium' | 'low';
  classification: string;
  risk_score: number;
  page?: number;
  confidence: number;
}

export interface AnalysisResult {
  summary: string;
  key_clauses: KeyClause[];
  document_type: string;
  total_pages: number;
  confidence: number;
  processing_time: number;
  word_count: number;
  analyzed_at: string;
  file_id?: string;
}

// Backend now responds as { formats: string[] }
export interface SupportedFormats {
  formats: string[];
}

export const analyzeDocument = async (file: File, onUploadProgress: (progress: number) => void): Promise<AnalysisResult> => {
  const formData = new FormData();
  formData.append('file', file);
  try {
    const response = await apiClient.post<AnalysisResult>('/analyze', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent) => {
        if (progressEvent.total) {
          const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          onUploadProgress(percentCompleted);
        }
      },
    });
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error) && error.response) {
      throw { 
        message: error.response.data.detail || 'Analysis failed.', 
        status: error.response.status,
        details: error.response.data
      } as ApiError;
    }
    throw { message: 'Analysis failed.' } as ApiError;
  }
};

export const exportAnalysis = async (fileId: string, format: 'pdf' | 'json') => {
  const startExportResponse = await apiClient.post<{ task_id: string }>(`/export/${fileId}/${format}`);
  const taskId = startExportResponse.data.task_id;

  while (true) {
    const pollResponse = await apiClient.get(`/export/${taskId}`, { responseType: 'blob' });

    if (pollResponse.headers['content-type'] === 'application/json') {
      const responseText = await (pollResponse.data as Blob).text();
      const statusResponse = JSON.parse(responseText);

      if (statusResponse.status === 'processing') {
        await new Promise(resolve => setTimeout(resolve, 2000)); // Wait 2 seconds
      } else {
        throw new Error('Export failed');
      }
    } else {
      const url = window.URL.createObjectURL(new Blob([pollResponse.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `analysis-report.${format}`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      return;
    }
  }
};

export const viewOriginalDocument = async (fileId: string) => {
  const response = await apiClient.get(`/documents/${fileId}`, { responseType: 'blob' });
  const fileURL = URL.createObjectURL(response.data);
  window.open(fileURL, '_blank');
};

export const getSupportedFormats = async (): Promise<SupportedFormats> => {
  const response = await apiClient.get<SupportedFormats>('/supported-formats');
  return response.data;
};
