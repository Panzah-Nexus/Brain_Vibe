import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { createProject } from '../services/api';

const ProjectList = ({ projects, onRefresh }) => {
  const [newProject, setNewProject] = useState({ project_id: '', name: '' });
  const [isCreating, setIsCreating] = useState(false);
  const [error, setError] = useState('');
  const [showForm, setShowForm] = useState(false);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setNewProject({ ...newProject, [name]: value });
    
    // Clear error when user types
    if (error) setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Validate inputs
    if (!newProject.project_id.trim() || !newProject.name.trim()) {
      setError('Both ID and Name are required.');
      return;
    }
    
    // Check if ID already exists
    const exists = projects.some(p => p.project_id === newProject.project_id);
    if (exists) {
      setError('A project with this ID already exists.');
      return;
    }
    
    try {
      setIsCreating(true);
      await createProject(newProject);
      
      // Reset form
      setNewProject({ project_id: '', name: '' });
      setShowForm(false);
      
      // Refresh projects list
      if (onRefresh) {
        onRefresh();
      }
    } catch (error) {
      console.error('Error creating project:', error);
      setError('Failed to create project. Please try again.');
    } finally {
      setIsCreating(false);
    }
  };

  return (
    <div>
      <div style={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center',
        marginBottom: '20px'
      }}>
        <h2 style={{ margin: 0 }}>Projects</h2>
        <button
          onClick={() => setShowForm(!showForm)}
          style={{
            padding: '8px 12px',
            backgroundColor: '#007bff',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer'
          }}
        >
          {showForm ? 'Cancel' : 'New Project'}
        </button>
      </div>
      
      {showForm && (
        <form 
          onSubmit={handleSubmit}
          style={{
            padding: '15px',
            backgroundColor: '#f8f9fa',
            borderRadius: '8px',
            marginBottom: '20px'
          }}
        >
          <div style={{ marginBottom: '15px' }}>
            <label 
              htmlFor="project_id"
              style={{ 
                display: 'block', 
                marginBottom: '5px',
                fontWeight: 'bold'
              }}
            >
              Project ID:
            </label>
            <input
              type="text"
              id="project_id"
              name="project_id"
              value={newProject.project_id}
              onChange={handleInputChange}
              style={{
                width: '100%',
                padding: '8px',
                borderRadius: '4px',
                border: '1px solid #ced4da'
              }}
              placeholder="unique-project-id"
            />
          </div>
          
          <div style={{ marginBottom: '15px' }}>
            <label 
              htmlFor="name"
              style={{ 
                display: 'block', 
                marginBottom: '5px',
                fontWeight: 'bold'
              }}
            >
              Project Name:
            </label>
            <input
              type="text"
              id="name"
              name="name"
              value={newProject.name}
              onChange={handleInputChange}
              style={{
                width: '100%',
                padding: '8px',
                borderRadius: '4px',
                border: '1px solid #ced4da'
              }}
              placeholder="My Awesome Project"
            />
          </div>
          
          {error && (
            <div style={{
              padding: '10px',
              backgroundColor: '#f8d7da',
              color: '#721c24',
              borderRadius: '4px',
              marginBottom: '15px'
            }}>
              {error}
            </div>
          )}
          
          <button
            type="submit"
            disabled={isCreating}
            style={{
              padding: '8px 16px',
              backgroundColor: '#28a745',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: isCreating ? 'not-allowed' : 'pointer',
              opacity: isCreating ? 0.7 : 1
            }}
          >
            {isCreating ? 'Creating...' : 'Create Project'}
          </button>
        </form>
      )}
      
      {projects.length === 0 ? (
        <p>No projects yet. Create your first project to get started!</p>
      ) : (
        <div style={{ 
          display: 'grid', 
          gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))',
          gap: '20px'
        }}>
          {projects.map(project => (
            <div
              key={project.project_id}
              style={{
                padding: '20px',
                backgroundColor: 'white',
                borderRadius: '8px',
                boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
                transition: 'transform 0.2s',
                ':hover': {
                  transform: 'translateY(-5px)'
                }
              }}
            >
              <h3 style={{ marginTop: 0 }}>{project.name}</h3>
              <p style={{ 
                color: '#6c757d',
                fontSize: '0.9rem'
              }}>
                ID: {project.project_id}
              </p>
              <p>
                {project.topic_ids ? `${project.topic_ids.length} topics` : '0 topics'}
              </p>
              <div style={{ marginTop: '15px' }}>
                <Link
                  to={`/projects/${project.project_id}`}
                  style={{
                    display: 'inline-block',
                    padding: '8px 12px',
                    backgroundColor: '#007bff',
                    color: 'white',
                    textDecoration: 'none',
                    borderRadius: '4px',
                    marginRight: '10px'
                  }}
                >
                  View Details
                </Link>
                <Link
                  to={`/projects/${project.project_id}/analyze`}
                  style={{
                    display: 'inline-block',
                    padding: '8px 12px',
                    backgroundColor: '#6c757d',
                    color: 'white',
                    textDecoration: 'none',
                    borderRadius: '4px'
                  }}
                >
                  Analyze Code
                </Link>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default ProjectList; 