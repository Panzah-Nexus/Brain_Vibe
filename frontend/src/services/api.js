import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || '';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Projects API
export const getProjects = async () => {
  const response = await api.get('/api/v1/projects');
  return response.data;
};

export const getProject = async (projectId) => {
  const response = await api.get(`/api/v1/projects/${projectId}`);
  return response.data;
};

export const createProject = async (projectData) => {
  const response = await api.post('/api/v1/projects', projectData);
  return response.data;
};

export const getProjectTopics = async (projectId) => {
  const response = await api.get(`/api/v1/projects/${projectId}/topics`);
  return response.data;
};

export const getProjectGraph = async (projectId) => {
  const response = await api.get(`/api/v1/projects/${projectId}/graph`);
  return response.data;
};

export const analyzeDiff = async (projectId, diffData) => {
  const response = await api.post(`/api/v1/projects/${projectId}/analyze-diff`, diffData);
  return response.data;
};

// Topics API
export const getTopics = async () => {
  const response = await api.get('/api/v1/topics');
  return response.data;
};

export const getTopic = async (topicId) => {
  const response = await api.get(`/api/v1/topics/${topicId}`);
  return response.data;
};

export const completeTopic = async (topicId, status) => {
  const response = await api.post(`/api/v1/topics/${topicId}/complete`, { status });
  return response.data;
};

export const getTopicProjects = async (topicId) => {
  const response = await api.get(`/api/v1/topics/${topicId}/projects`);
  return response.data;
};

// Master Brain API
export const getMasterGraph = async () => {
  const response = await api.get('/api/v1/master-graph');
  return response.data;
};

export default api; 