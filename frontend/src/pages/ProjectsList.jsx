import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import apiService from '../services/api';

const ProjectsList = () => {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
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

    fetchProjects();
  }, []);

  if (loading) return <div>Loading projects...</div>;
  if (error) return <div className="error">{error}</div>;

  return (
    <div className="projects-list">
      <h1>Your Learning Projects</h1>
      
      {projects.length === 0 ? (
        <p>No projects found. Create your first project to get started!</p>
      ) : (
        <div className="projects-grid">
          {projects.map(project => (
            <div key={project.project_id} className="project-card">
              <h2>{project.name}</h2>
              <p>{project.description}</p>
              <div className="card-footer">
                <Link to={`/projects/${project.project_id}`}>
                  View Details
                </Link>
                {/* Placeholder for future project stats/metrics */}
                <div className="project-stats">
                  {/* Will show count of topics, learned vs not learned */}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
      
      {/* Placeholder for project creation UI */}
      <div className="create-project">
        <p>Ready to track learning in a new project?</p>
        <button>Create Project</button>
      </div>
    </div>
  );
};

export default ProjectsList; 