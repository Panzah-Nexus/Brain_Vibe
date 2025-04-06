import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import apiService from '../services/api';

const ProjectsList = () => {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [newProject, setNewProject] = useState({ name: '', description: '' });
  const navigate = useNavigate();

  useEffect(() => {
    fetchProjects();
  }, []);

  const fetchProjects = async () => {
    try {
      setLoading(true);
      const data = await apiService.getProjects();
      setProjects(data.results || []);
      setLoading(false);
    } catch (err) {
      console.error('Error fetching projects:', err);
      setError('Failed to load projects. Please try again later.');
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
        <button onClick={() => setShowCreateDialog(true)}>Create New Project</button>
      </header>
      
      {error && (
        <div className="error-message">
          <p>{error}</p>
          <button onClick={() => setError(null)}>Dismiss</button>
        </div>
      )}
      
      {projects.length === 0 ? (
        <div className="empty-state">
          <p>No projects found. Create your first project to get started!</p>
          <button onClick={() => setShowCreateDialog(true)}>Create Project</button>
        </div>
      ) : (
        <div className="projects-grid">
          {projects.map(project => (
            <Link 
              key={project.project_id} 
              to={`/projects/${project.project_id}`}
              className="project-card"
            >
              <h2>{project.name}</h2>
              <p>{project.description}</p>
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