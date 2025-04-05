import React, { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { getProject, getProjectGraph } from '../services/api';
import GraphVisualization from '../components/GraphVisualization';
import TopicDetail from '../components/TopicDetail';

const ProjectPage = () => {
  const { projectId } = useParams();
  const navigate = useNavigate();
  
  const [project, setProject] = useState(null);
  const [graphData, setGraphData] = useState({ nodes: [], edges: [] });
  const [selectedTopic, setSelectedTopic] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  // Load project data when the component mounts
  useEffect(() => {
    fetchProjectData();
  }, [projectId]);

  const fetchProjectData = async () => {
    try {
      setIsLoading(true);
      
      // Fetch the project details
      const projectData = await getProject(projectId);
      setProject(projectData);
      
      // Fetch the project graph
      const graphData = await getProjectGraph(projectId);
      setGraphData(graphData);
      
      setError('');
    } catch (error) {
      console.error('Error fetching project data:', error);
      setError('Failed to load project data. Please try again later.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleNodeClick = (nodeData) => {
    setSelectedTopic(nodeData);
  };

  const handleTopicStatusChange = (updatedTopic) => {
    // Update the graphData with the updated topic
    setGraphData(prevGraphData => {
      const nodes = prevGraphData.nodes.map(node => {
        if (node.id === updatedTopic.topic_id) {
          return {
            ...node,
            status: updatedTopic.status
          };
        }
        return node;
      });
      
      return {
        ...prevGraphData,
        nodes
      };
    });
    
    // Update the selected topic
    setSelectedTopic(updatedTopic);
  };

  if (isLoading) {
    return <div>Loading project data...</div>;
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
          onClick={fetchProjectData}
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
        justifyContent: 'space-between', 
        alignItems: 'center',
        marginBottom: '20px'
      }}>
        <div>
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
          <span style={{ marginLeft: '10px' }}>{project.name}</span>
        </div>
        
        <div>
          <Link
            to={`/projects/${projectId}/analyze`}
            style={{
              display: 'inline-block',
              padding: '8px 12px',
              backgroundColor: '#007bff',
              color: 'white',
              textDecoration: 'none',
              borderRadius: '4px'
            }}
          >
            Analyze Code
          </Link>
        </div>
      </div>
      
      <h1>{project.name}</h1>
      <p>Project ID: {project.project_id}</p>
      <p>Topics: {project.topic_ids.length}</p>
      
      <div style={{ 
        display: 'flex', 
        height: 'calc(100vh - 300px)',
        minHeight: '500px',
        marginTop: '30px',
        gap: '20px'
      }}>
        <div style={{ 
          flex: 2, 
          border: '1px solid #dee2e6', 
          borderRadius: '8px',
          overflow: 'hidden'
        }}>
          <GraphVisualization 
            graphData={graphData} 
            onNodeClick={handleNodeClick} 
          />
        </div>
        
        <div style={{ flex: 1 }}>
          {selectedTopic ? (
            <TopicDetail 
              topic={selectedTopic} 
              onStatusChange={handleTopicStatusChange} 
            />
          ) : (
            <div style={{
              padding: '20px',
              backgroundColor: '#f8f9fa',
              borderRadius: '8px',
              textAlign: 'center'
            }}>
              <p>Select a topic in the graph to view details.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ProjectPage; 