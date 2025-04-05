import React, { useState, useEffect } from 'react';
import ProjectList from '../components/ProjectList';
import { getProjects } from '../services/api';

const HomePage = () => {
  const [projects, setProjects] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  // Load projects when the component mounts
  useEffect(() => {
    fetchProjects();
  }, []);

  const fetchProjects = async () => {
    try {
      setIsLoading(true);
      const data = await getProjects();
      setProjects(data);
      setError('');
    } catch (error) {
      console.error('Error fetching projects:', error);
      setError('Failed to load projects. Please try again later.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '0 20px' }}>
      <div style={{ marginBottom: '30px' }}>
        <h1>AI-Facilitated Code & Learning Graph System</h1>
        <p>
          Monitor your code changes, analyze new programming concepts, and track your learning journey.
        </p>
      </div>
      
      {isLoading ? (
        <div>Loading projects...</div>
      ) : error ? (
        <div style={{
          padding: '15px',
          backgroundColor: '#f8d7da',
          color: '#721c24',
          borderRadius: '4px',
          marginBottom: '20px'
        }}>
          {error}
          <button
            onClick={fetchProjects}
            style={{
              marginLeft: '15px',
              padding: '5px 10px',
              backgroundColor: '#dc3545',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer'
            }}
          >
            Retry
          </button>
        </div>
      ) : (
        <ProjectList projects={projects} onRefresh={fetchProjects} />
      )}
    </div>
  );
};

export default HomePage; 