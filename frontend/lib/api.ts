import axios from 'axios';
import {
  AuthTokenResponse,
  UserRegisterData,
  UserLoginData,
  UserProfile,
  InspectionResult,
  AnalyticsSummary,
  ReportResult,
} from '@/types';

const rawUrl = (process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1').trim().replace(/\/$/, '');
const API_BASE_URL = rawUrl.endsWith('/api/v1') ? rawUrl : `${rawUrl}/api/v1`;

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request Interceptor: Attach JWT Token if available
apiClient.interceptors.request.use(
  (config) => {
    if (typeof window !== 'undefined') {
      const token = localStorage.getItem('token');
      if (token && config.headers) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response Interceptor: Handle 401 Unauthorized globally
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      if (typeof window !== 'undefined') {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        if (!window.location.pathname.includes('/login')) {
          window.location.href = '/login';
        }
      }
    }
    return Promise.reject(error);
  }
);

// Authentication Endpoints
export const authApi = {
  register: async (data: UserRegisterData): Promise<UserProfile> => {
    const res = await apiClient.post<UserProfile>('/auth/register', data);
    return res.data;
  },
  login: async (data: UserLoginData): Promise<AuthTokenResponse> => {
    const res = await apiClient.post<AuthTokenResponse>('/auth/login', data);
    return res.data;
  },
  getProfile: async (): Promise<UserProfile> => {
    const res = await apiClient.get<UserProfile>('/auth/me');
    return res.data;
  },
  forgotPassword: async (email: string): Promise<{ message: string }> => {
    const res = await apiClient.post<{ message: string }>('/auth/forgot-password', { email });
    return res.data;
  },
};

// Inspection & AI Endpoints
export const inspectApi = {
  analyzeImage: async (file: File): Promise<InspectionResult> => {
    const formData = new FormData();
    formData.append('file', file);

    const res = await apiClient.post<InspectionResult>('/inspect/analyze', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return res.data;
  },
  getHistory: async (limit: number = 50): Promise<InspectionResult[]> => {
    const res = await apiClient.get<InspectionResult[]>(`/inspect/history?limit=${limit}`);
    return res.data;
  },
  getDetails: async (inspectionId: string): Promise<InspectionResult> => {
    const res = await apiClient.get<InspectionResult>(`/inspect/${inspectionId}`);
    return res.data;
  },
  generateReport: async (inspectionId: string): Promise<ReportResult> => {
    const res = await apiClient.post<ReportResult>(`/inspect/${inspectionId}/report`);
    return res.data;
  },
};

// Analytics Endpoints
export const analyticsApi = {
  getSummary: async (): Promise<AnalyticsSummary> => {
    const res = await apiClient.get<AnalyticsSummary>('/analytics/summary');
    return res.data;
  },
};