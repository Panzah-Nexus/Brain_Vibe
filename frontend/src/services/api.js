import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

// Create axios instance with base config
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// API service functions
const apiService = {
  // Projects
  async getProjects() {
    const response = await apiClient.get('/projects/');
    return response.data;
  },

  async getProject(projectId) {
    const response = await apiClient.get(`/projects/${projectId}/`);
    return response.data;
  },

  async getProjectTopics(projectId) {
    const response = await apiClient.get(`/projects/${projectId}/topics/`);
    return response.data;
  },

  async analyzeProjectDiff(projectId, repoPath) {
    const response = await apiClient.post(`/projects/${projectId}/analyze-diff/`, { repo_path: repoPath });
    return response.data;
  },

  // Topics
  async getTopics() {
    const response = await apiClient.get('/topics/');
    return response.data;
  },

  async markTopicAsLearned(topicId) {
    const response = await apiClient.post(`/topics/${topicId}/complete/`);
    return response.data;
  },

  // Master Brain
  async getMasterGraph() {
    const response = await apiClient.get('/master-graph/');
    return response.data;
  },
};

export default apiService; 