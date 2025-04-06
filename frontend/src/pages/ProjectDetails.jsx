import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import apiService from '../services/api';

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
      try {
        setLoading(true);
        
        // Fetch project details
        const projectData = await apiService.getProject(projectId);
        setProject(projectData);
        
        // Fetch project topics
        const topicsData = await apiService.getProjectTopics(projectId);
        setTopics(topicsData);
        
        setLoading(false);
      } catch (err) {
        console.error('Error fetching project data:', err);
        setError('Failed to load project data. Please try again later.');
        setLoading(false);
      }
    };

    fetchProjectData();
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
        <Link to="/projects">← Back to Projects</Link>
      </header>
      
      <section className="analyze-section">
        <h2>Analyze Repository</h2>
        <form onSubmit={handleAnalyzeRepo}>
          <input 
            type="text" 
            value={repoPath} 
            onChange={(e) => setRepoPath(e.target.value)}
            placeholder="Enter repository path"
            disabled={analyzing}
          />
          <button type="submit" disabled={analyzing}>
            {analyzing ? 'Analyzing...' : 'Analyze Changes'}
          </button>
        </form>
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
    </div>
  );
};

export default ProjectDetails; 