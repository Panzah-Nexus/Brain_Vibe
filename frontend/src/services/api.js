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
    try {
      console.log('Calling API to fetch projects');
      // Use explicit URL with trailing slash
      const response = await apiClient.get('/projects/');
      console.log('Projects API response:', response);
      
      // Handle Django REST Framework pagination
      if (response.data && typeof response.data === 'object') {
        if (response.data.results && Array.isArray(response.data.results)) {
          // It's paginated, return the results array
          return response.data.results;
        } else if (!response.data.results && Object.keys(response.data).length > 0) {
          // It's not paginated but it's an object, check if it might be an array of objects
          if (Array.isArray(response.data)) {
            return response.data;
          }
          // It's a single object, wrap it in an array
          return [response.data];
        }
      }
      
      // Return empty array if none of the above conditions match
      return [];
    } catch (error) {
      console.error('Error fetching projects from API:', error);
      // Return empty array on error to avoid breaking the UI
      return [];
    }
  },

  async createProject(projectData) {
    const response = await apiClient.post('/projects/', projectData);
    return response.data;
  },

  async getProject(projectId) {
    if (!projectId) {
      console.error('No project ID provided to getProject');
      return null;
    }
    
    try {
      console.log(`Fetching project with ID: ${projectId}`);
      const response = await apiClient.get(`/projects/${projectId}/`);
      console.log(`Project fetch response:`, response);
      
      // Ensure we have valid data
      if (response.data) {
        return response.data;
      }
      
      console.error('Empty response data from project fetch');
      return null;
    } catch (error) {
      console.error(`Error fetching project ${projectId}:`, error);
      throw error; // We still throw here because this is a critical failure
    }
  },

  async getProjectTopics(projectId) {
    try {
      console.log(`Fetching topics for project ID: ${projectId}`);
      const response = await apiClient.get(`/projects/${projectId}/topics/`);
      console.log(`Project topics response:`, response);
      
      // Handle potential response formats (array or object with data)
      if (response.data) {
        if (Array.isArray(response.data)) {
          return response.data;
        } else if (response.data.results && Array.isArray(response.data.results)) {
          return response.data.results;
        }
      }
      
      // Default to empty array if no valid data format found
      return [];
    } catch (error) {
      console.error(`Error fetching topics for project ${projectId}:`, error);
      // Return empty array on error to avoid breaking the UI
      return [];
    }
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