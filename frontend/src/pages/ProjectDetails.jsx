import { useState, useEffect, useRef } from 'react';
import { useParams, Link } from 'react-router-dom';
import apiService from '../services/api';
import GraphVisualization from '../components/GraphVisualization';

// Debug component to show raw API data
const DebugInfo = ({ project, topics, error }) => {
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
      
      <h4>Project Data:</h4>
      <pre style={{ background: '#f5f5f5', padding: '10px', overflow: 'auto' }}>
        {JSON.stringify(project, null, 2)}
      </pre>
      
      <h4>Topics Data:</h4>
      <pre style={{ background: '#f5f5f5', padding: '10px', overflow: 'auto' }}>
        {JSON.stringify(topics, null, 2)}
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

// Project ID Display and Copy component
const ProjectIdDisplay = ({ projectId }) => {
  const [copied, setCopied] = useState(false);
  const idRef = useRef(null);

  const copyToClipboard = () => {
    navigator.clipboard.writeText(projectId)
      .then(() => {
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
      })
      .catch(err => {
        console.error('Failed to copy: ', err);
      });
  };

  return (
    <div className="project-id-display">
      <h2>Project ID</h2>
      <p className="project-id-description">
        Use this ID to link your local repository with the CLI tool:
      </p>
      <div className="project-id-container">
        <code ref={idRef} className="project-id">{projectId}</code>
        <button 
          onClick={copyToClipboard} 
          className="copy-button"
          title="Copy to clipboard"
        >
          {copied ? 'Copied!' : 'Copy'}
        </button>
      </div>
    </div>
  );
};

const ProjectDetails = () => {
  const { projectId } = useParams();
  const [project, setProject] = useState(null);
  const [topics, setTopics] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [repoPath, setRepoPath] = useState('');
  const [analyzing, setAnalyzing] = useState(false);

  useEffect(() => {
    const fetchProjectData = async () => {
      if (!projectId) {
        setError("No project ID provided");
        setLoading(false);
        return;
      }
      
      try {
        setLoading(true);
        console.log(`Fetching project with ID: ${projectId}`);
        
        // Fetch project details
        const projectData = await apiService.getProject(projectId);
        console.log('Project data:', projectData);
        setProject(projectData);
        
        // Fetch project topics (API service now handles errors)
        const topicsData = await apiService.getProjectTopics(projectId);
        console.log('Topics data:', topicsData);
        setTopics(topicsData);
        
        setLoading(false);
      } catch (err) {
        console.error('Error fetching project data:', err);
        setError(`Failed to load project data: ${err.message || 'Unknown error'}`);
        setLoading(false);
      }
    };

    if (projectId) {
      fetchProjectData();
    }
  }, [projectId]);

  const handleAnalyzeRepo = async (e) => {
    e.preventDefault();
    if (!repoPath.trim()) return;
    
    try {
      setAnalyzing(true);
      const result = await apiService.analyzeProjectDiff(projectId, repoPath);
      
      // Refresh topics after analysis
      const topicsData = await apiService.getProjectTopics(projectId);
      setTopics(topicsData);
      
      setAnalyzing(false);
      setRepoPath('');
      // Show success message - this would be a proper notification in a real app
      alert(`Analysis complete! Found ${result.topics_created} new topics.`);
    } catch (err) {
      console.error('Error analyzing repo:', err);
      setAnalyzing(false);
      alert('Failed to analyze repository. Please check the path and try again.');
    }
  };

  const handleMarkAsLearned = async (topicId) => {
    try {
      await apiService.markTopicAsLearned(topicId);
      
      // Update local state to show the change immediately
      setTopics(topics.map(topic => 
        topic.topic_id === topicId 
          ? { ...topic, status: 'learned' } 
          : topic
      ));
      
    } catch (err) {
      console.error('Error marking topic as learned:', err);
      alert('Failed to mark topic as learned. Please try again.');
    }
  };

  if (loading) return <div>Loading project details...</div>;
  if (error) return <div className="error">{error}</div>;
  if (!project) return <div>Project not found</div>;

  return (
    <div className="project-details">
      <header>
        <h1>{project.name}</h1>
        <p>{project.description}</p>
        <div className="project-header-actions">
          <ProjectIdDisplay projectId={projectId} />
          <Link to="/projects" className="back-link">← Back to Projects</Link>
        </div>
      </header>
      
      {/* Add Knowledge Graph Visualization */}
      <section className="knowledge-graph-section">
        <h2>Knowledge Graph</h2>
        <p>Explore topics and their relationships for this project</p>
        <GraphVisualization 
          topics={topics}
          onMarkAsLearned={handleMarkAsLearned}
          height="600px"
        />
      </section>
      
      <section className="analyze-section">
        <h2>Analyze Repository</h2>
        <div className="analyze-options">
          <div className="option-card">
            <h3>Option 1: Analyze Local Repository</h3>
            <p>Enter a local repository path to analyze changes:</p>
            <form onSubmit={handleAnalyzeRepo}>
              <input 
                type="text" 
                value={repoPath} 
                onChange={(e) => setRepoPath(e.target.value)}
                placeholder="Enter local repository path"
                disabled={analyzing}
              />
              <button type="submit" disabled={analyzing}>
                {analyzing ? 'Analyzing...' : 'Analyze Changes'}
              </button>
            </form>
          </div>
          
          <div className="option-card">
            <h3>Option 2: Use CLI Tool (Recommended)</h3>
            <p>Track changes in real-time with the BrainVibe CLI:</p>
            <div className="cli-instructions">
              <h4>1. Install the CLI tool</h4>
              <pre>cd cli<br/>pip install -e .</pre>
              
              <h4>2. Initialize BrainVibe in your project</h4>
              <pre>cd /path/to/your/project<br/>brainvibe init --project-id {projectId}</pre>
              
              <h4>3. Start tracking changes</h4>
              <pre>brainvibe track --watch</pre>
              
              <p>This will continuously track changes and update topics automatically.</p>
              <p><a href="/cli-docs" className="link">Read CLI documentation →</a></p>
            </div>
          </div>
        </div>
      </section>
      
      <section className="topics-section">
        <h2>Learning Topics</h2>
        {topics.length === 0 ? (
          <p>No topics found for this project yet. Analyze a repository to discover topics!</p>
        ) : (
          <div className="topics-list">
            {topics.map(topic => (
              <div 
                key={topic.topic_id} 
                className={`topic-card ${topic.status}`}
              >
                <h3>{topic.title}</h3>
                <p>{topic.description}</p>
                <div className="topic-status">
                  Status: <span>{topic.status.replace('_', ' ')}</span>
                </div>
                {topic.status !== 'learned' && (
                  <button 
                    onClick={() => handleMarkAsLearned(topic.topic_id)}
                    className="mark-learned-btn"
                  >
                    Mark as Learned
                  </button>
                )}
                {/* Placeholder for showing dependencies/prerequisites */}
                <div className="topic-dependencies">
                  {/* Will show related topics */}
                </div>
              </div>
            ))}
          </div>
        )}
      </section>
      
      {/* Placeholder for future graph visualization */}
      <section className="graph-visualization">
        <h2>Topic Graph Visualization</h2>
        <p>Graph visualization will be implemented in future versions</p>
        <div className="graph-placeholder">
          {/* This will be replaced with an actual graph visualization */}
        </div>
      </section>
      
      <DebugInfo project={project} topics={topics} error={error} />
    </div>
  );
};

export default ProjectDetails; 