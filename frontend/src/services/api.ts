import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: `${API_URL}/api/v1`,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default api;

// Auth API
export const authAPI = {
  login: (email: string, password: string) =>
    api.post('/auth/login', { email, password }),
  getCurrentUser: () => api.get('/users/me'),
};

// Patients API
export const patientsAPI = {
  list: (params?: any) => api.get('/patients/', { params }),
  create: (data: any) => api.post('/patients/', data),
  get: (id: number) => api.get(`/patients/${id}`),
  update: (id: number, data: any) => api.patch(`/patients/${id}`, data),
  getTimeline: (id: number) => api.get(`/patients/${id}/timeline`),
};

// Appointments API
export const appointmentsAPI = {
  list: (params?: any) => api.get('/appointments/', { params }),
  create: (data: any) => api.post('/appointments/', data),
  get: (id: number) => api.get(`/appointments/${id}`),
  update: (id: number, data: any) => api.patch(`/appointments/${id}`, data),
  reschedule: (id: number, new_date: string, notes?: string) =>
    api.post(`/appointments/${id}/reschedule`, { new_date, notes }),
  listMissed: (days_ago?: number) =>
    api.get('/appointments/missed/list', { params: { days_ago } }),
};

// Follow-ups API
export const followUpsAPI = {
  listPlans: (params?: any) => api.get('/follow-ups/plans', { params }),
  createPlan: (data: any) => api.post('/follow-ups/plans', data),
  getPlan: (id: number) => api.get(`/follow-ups/plans/${id}`),
  updatePlan: (id: number, data: any) => api.patch(`/follow-ups/plans/${id}`, data),
  listTasks: (params?: any) => api.get('/follow-ups/tasks', { params }),
  createTask: (plan_id: number, data: any) =>
    api.post(`/follow-ups/tasks?plan_id=${plan_id}`, data),
  updateTask: (id: number, data: any) => api.patch(`/follow-ups/tasks/${id}`, data),
  getPriorityWorklist: (params?: any) =>
    api.get('/follow-ups/worklist/priority', { params }),
};

// Consultations API
export const consultationsAPI = {
  list: (params?: any) => api.get('/consultations/', { params }),
  create: (data: any) => api.post('/consultations/', data),
  get: (id: number) => api.get(`/consultations/${id}`),
  update: (id: number, data: any) => api.patch(`/consultations/${id}`, data),
  generateAISummary: (id: number) =>
    api.post(`/consultations/${id}/ai-summary`),
};

// Prescriptions API
export const prescriptionsAPI = {
  create: (data: any) => api.post('/consultations/prescriptions', data),
  get: (id: number) => api.get(`/consultations/prescriptions/${id}`),
  update: (id: number, data: any) =>
    api.patch(`/consultations/prescriptions/${id}`, data),
  downloadPDF: (id: number) =>
    api.get(`/consultations/prescriptions/${id}/pdf`, { responseType: 'blob' }),
};

// Analytics API
export const analyticsAPI = {
  getDashboard: (params?: any) => api.get('/analytics/dashboard', { params }),
  getUnresolvedCases: () => api.get('/analytics/unresolved-cases'),
  getTrends: (days?: number) => api.get('/analytics/trends', { params: { days } }),
};

// Users API
export const usersAPI = {
  list: (params?: any) => api.get('/users/', { params }),
  create: (data: any) => api.post('/users/', data),
  get: (id: number) => api.get(`/users/${id}`),
  update: (id: number, data: any) => api.patch(`/users/${id}`, data),
  listDoctors: () => api.get('/users/doctors/list'),
};
