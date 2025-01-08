import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:5000/api',
});

export interface Document {
  name: string;
  content: string;
  created_at: string;
  company?: string;
  position?: string;
}

export interface Biography {
  version: number;
  content: string;
  created_at: string;
  notes?: string;
}

export interface AIPrompt {
  name: string;
  content: string;
  description?: string;
  created_at: string;
  updated_at: string;
}

export const documentsApi = {
  list: (type: string) => api.get<Document[]>(`/documents/${type}`),
  get: (type: string, name: string) => api.get<Document>(`/documents/${type}/${name}`),
  create: (type: string, data: { name: string; content: string; metadata?: any }) =>
    api.post(`/documents/${type}`, data),
  delete: (type: string, name: string) => api.delete(`/documents/${type}/${name}`),
};

export const biographyApi = {
  get: () => api.get<Biography>('/biography'),
  update: (content: string, notes?: string) => api.post('/biography', { content, notes }),
  getVersions: () => api.get<Biography[]>('/biography/versions'),
  getVersion: (version: number) => api.get<Biography>(`/biography/${version}`),
};

export const promptsApi = {
  list: () => api.get<AIPrompt[]>('/prompts'),
  get: (name: string) => api.get<AIPrompt>(`/prompts/${name}`),
  save: (name: string, content: string, description?: string) =>
    api.post(`/prompts/${name}`, { content, description }),
};

export const generatorApi = {
  generate: (data: {
    resume_name: string;
    job_description_name: string;
    sample_letter_name: string;
    preferences?: string;
  }) => api.post('/generate-cover-letter', data),
};

export default api; 