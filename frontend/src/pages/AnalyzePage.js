import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { getProject } from '../services/api';
import CodeDiffAnalyzer from '../components/CodeDiffAnalyzer';

const AnalyzePage = () => {
  const { projectId } = useParams();
  
  const [project, setProject] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  // Load project data when the component mounts
  useEffect(() => {
    fetchProject();
  }, [projectId]);

  const fetchProject = async () => {
    try {
      setIsLoading(true);
      const data = await getProject(projectId);
      setProject(data);
      setError('');
    } catch (error) {
      console.error('Error fetching project:', error);
      setError('Failed to load project. Please try again later.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleAnalysisComplete = () => {
    // Could add additional logic here if needed
    console.log('Analysis completed');
  };

  if (isLoading) {
    return <div>Loading project...</div>;
  }

  if (error) {
    return (
      <div style={{
        padding: '15px',
        backgroundColor: '#f8d7da',
        color: '#721c24',
        borderRadius: '4px',
        marginBottom: '20px'
      }}>
        {error}
        <button
          onClick={fetchProject}
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
        <Link
          to="/"
          style={{
            marginLeft: '10px',
            padding: '5px 10px',
            backgroundColor: '#6c757d',
            color: 'white',
            textDecoration: 'none',
            borderRadius: '4px'
          }}
        >
          Back to Projects
        </Link>
      </div>
    );
  }

  if (!project) {
    return <div>Project not found.</div>;
  }

  return (
    <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '0 20px' }}>
      <div style={{ 
        display: 'flex', 
        alignItems: 'center',
        marginBottom: '20px'
      }}>
        <Link 
          to="/"
          style={{
            color: '#6c757d',
            textDecoration: 'none',
            marginRight: '10px'
          }}
        >
          Projects
        </Link>
        <span style={{ color: '#6c757d' }}>/</span>
        <Link 
          to={`/projects/${projectId}`}
          style={{
            color: '#6c757d',
            textDecoration: 'none',
            margin: '0 10px'
          }}
        >
          {project.name}
        </Link>
        <span style={{ color: '#6c757d' }}>/</span>
        <span style={{ marginLeft: '10px' }}>Analyze Code</span>
      </div>
      
      <h1>Analyze Code for {project.name}</h1>
      
      <div style={{ marginTop: '30px' }}>
        <CodeDiffAnalyzer 
          projectId={projectId} 
          onAnalysisComplete={handleAnalysisComplete} 
        />
      </div>
    </div>
  );
};

export default AnalyzePage; 