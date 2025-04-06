import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import apiService from '../services/api';

// Debug component to show raw API data
const DebugInfo = ({ data, error }) => {
  const [showDebug, setShowDebug] = useState(false);
  
  if (!showDebug) {
    return (
      <button 
        onClick={() => setShowDebug(true)}
        style={{ 
          position: 'fixed', 
          bottom: '10px', 
          right: '10px',
          padding: '5px 10px',
          background: '#f0f0f0',
          border: '1px solid #ccc',
          borderRadius: '4px',
          cursor: 'pointer',
          fontSize: '12px'
        }}
      >
        Show Debug Info
      </button>
    );
  }
  
  return (
    <div style={{
      position: 'fixed',
      bottom: '10px',
      right: '10px',
      width: '400px',
      maxHeight: '400px',
      overflow: 'auto',
      background: '#fff',
      border: '1px solid #ccc',
      padding: '10px',
      borderRadius: '4px',
      boxShadow: '0 0 10px rgba(0,0,0,0.1)',
      zIndex: 1000,
      fontSize: '12px'
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '10px' }}>
        <h3 style={{ margin: 0 }}>Debug Info</h3>
        <button 
          onClick={() => setShowDebug(false)}
          style={{
            background: 'none',
            border: 'none',
            cursor: 'pointer',
            fontSize: '16px'
          }}
        >
          ×
        </button>
      </div>
      
      <h4>Projects Data:</h4>
      <pre style={{ background: '#f5f5f5', padding: '10px', overflow: 'auto' }}>
        {JSON.stringify(data, null, 2)}
      </pre>
      
      {error && (
        <>
          <h4>Error:</h4>
          <pre style={{ background: '#fff0f0', padding: '10px', overflow: 'auto', color: 'red' }}>
            {JSON.stringify(error, null, 2)}
          </pre>
        </>
      )}
    </div>
  );
};

const ProjectsList = () => {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [newProject, setNewProject] = useState({ name: '', description: '' });
  const [rawData, setRawData] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    fetchProjects();
  }, []);

  const fetchProjects = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // The API service now handles all the data formatting
      const projectsData = await apiService.getProjects();
      console.log('Fetched projects data:', projectsData);
      
      // Store raw data for debugging
      setRawData(projectsData);
      
      // Set the projects directly (API service now returns properly formatted array)
      setProjects(projectsData || []);
      
      setLoading(false);
    } catch (err) {
      console.error('Error fetching projects:', err);
      setError('Failed to load projects. Please try again later.');
      setRawData(null);
      setProjects([]);
      setLoading(false);
    }
  };

  const handleCreateProject = async (e) => {
    e.preventDefault();
    try {
      setError(null);
      console.log('Creating project with data:', newProject);
      const response = await apiService.createProject(newProject);
      console.log('Project creation response:', response);
      
      if (response && response.project_id) {
        setProjects([...projects, response]);
        setShowCreateDialog(false);
        setNewProject({ name: '', description: '' });
        navigate(`/projects/${response.project_id}`);
      } else {
        const errorMsg = 'Failed to create project. Invalid response from server.';
        console.error(errorMsg, response);
        setError(errorMsg);
      }
    } catch (err) {
      console.error('Error creating project:', err);
      const errorMsg = err.response?.data?.detail || 
                      err.response?.data?.message || 
                      err.message || 
                      'Failed to create project. Please try again.';
      setError(errorMsg);
    }
  };

  if (loading) return <div>Loading projects...</div>;

  return (
    <div className="projects-list">
      <header>
        <h1>Your Learning Projects</h1>
        <div className="header-actions">
          <button 
            onClick={fetchProjects} 
            disabled={loading}
            style={{ marginRight: '10px' }}
          >
            {loading ? 'Refreshing...' : 'Refresh Projects'}
          </button>
          <button onClick={() => setShowCreateDialog(true)}>Create New Project</button>
        </div>
      </header>
      
      {error && (
        <div className="error-message">
          <p>{error}</p>
          <button onClick={() => setError(null)}>Dismiss</button>
        </div>
      )}
      
      <div className="debug-section" style={{ marginBottom: '20px', padding: '10px', background: '#f5f5f5', borderRadius: '4px' }}>
        <h3>Projects Data Overview</h3>
        <p><strong>Loading:</strong> {loading ? 'Yes' : 'No'}</p>
        <p><strong>Projects Count:</strong> {projects?.length || 0}</p>
        <p><strong>Raw Data Type:</strong> {rawData ? (Array.isArray(rawData) ? 'Array' : typeof rawData) : 'null'}</p>
        {rawData && !Array.isArray(rawData) && <p><strong>Has 'results' property:</strong> {rawData.results ? 'Yes' : 'No'}</p>}
      </div>
      
      {loading ? (
        <div className="loading">Loading projects...</div>
      ) : projects.length === 0 ? (
        <div className="empty-state">
          <p>No projects found. Create your first project to get started!</p>
          <button onClick={() => setShowCreateDialog(true)}>Create Project</button>
        </div>
      ) : (
        <div className="projects-grid">
          {projects.map(project => (
            <Link 
              key={project.project_id || project.id} 
              to={`/projects/${project.project_id || project.id}`}
              className="project-card"
            >
              <h2>{project.name}</h2>
              <p>{project.description}</p>
              <div className="project-id-label">
                Project ID: <code>{project.project_id || project.id}</code>
              </div>
              <div className="card-footer">
                <span>View Details →</span>
                <div className="project-stats">
                  {/* Will show count of topics, learned vs not learned */}
                </div>
              </div>
            </Link>
          ))}
        </div>
      )}
      
      <DebugInfo data={rawData} error={error} />
      
      {showCreateDialog && (
        <div className="modal-overlay">
          <div className="modal">
            <h2>Create New Project</h2>
            {error && <div className="error-message">{error}</div>}
            <form onSubmit={handleCreateProject}>
              <div className="form-group">
                <label htmlFor="project-name">Project Name</label>
                <input
                  id="project-name"
                  type="text"
                  value={newProject.name}
                  onChange={(e) => setNewProject({...newProject, name: e.target.value})}
                  required
                  placeholder="Enter project name"
                />
              </div>
              <div className="form-group">
                <label htmlFor="project-description">Description</label>
                <textarea
                  id="project-description"
                  value={newProject.description}
                  onChange={(e) => setNewProject({...newProject, description: e.target.value})}
                  required
                  placeholder="Enter project description"
                />
              </div>
              <div className="modal-actions">
                <button type="button" onClick={() => setShowCreateDialog(false)}>Cancel</button>
                <button type="submit">Create Project</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default ProjectsList; 