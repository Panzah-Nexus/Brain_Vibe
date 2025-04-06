import { useState, useEffect } from 'react';
import apiService from '../services/api';
import GraphVisualization from '../components/GraphVisualization';

const MasterBrainPage = () => {
  const [topics, setTopics] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filter, setFilter] = useState('all'); // 'all', 'learned', 'not_learned', 'in_progress'

  useEffect(() => {
    const fetchMasterGraph = async () => {
      try {
        setLoading(true);
        const data = await apiService.getMasterGraph();
        setTopics(data.topics || []);
        setLoading(false);
      } catch (err) {
        console.error('Error fetching master graph:', err);
        setError('Failed to load master brain. Please try again later.');
        setLoading(false);
      }
    };

    fetchMasterGraph();
  }, []);

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

  const filteredTopics = topics.filter(topic => {
    if (filter === 'all') return true;
    return topic.status === filter;
  });

  if (loading) return <div>Loading master brain...</div>;
  if (error) return <div className="error">{error}</div>;

  return (
    <div className="master-brain">
      <header>
        <h1>Master Brain</h1>
        <p>All learning topics across your projects</p>
      </header>
      
      <section className="graph-visualization-section">
        <h2>Knowledge Graph Visualization</h2>
        <GraphVisualization 
          topics={topics}
          onMarkAsLearned={handleMarkAsLearned}
          height="600px"
        />
      </section>
      
      <div className="filters">
        <button 
          className={filter === 'all' ? 'active' : ''} 
          onClick={() => setFilter('all')}
        >
          All Topics
        </button>
        <button 
          className={filter === 'not_learned' ? 'active' : ''} 
          onClick={() => setFilter('not_learned')}
        >
          Not Learned
        </button>
        <button 
          className={filter === 'in_progress' ? 'active' : ''} 
          onClick={() => setFilter('in_progress')}
        >
          In Progress
        </button>
        <button 
          className={filter === 'learned' ? 'active' : ''} 
          onClick={() => setFilter('learned')}
        >
          Learned
        </button>
      </div>
      
      <section className="master-topics">
        <h2>Topics ({filteredTopics.length})</h2>
        {filteredTopics.length === 0 ? (
          <p>No topics found matching the selected filter.</p>
        ) : (
          <div className="topics-grid">
            {filteredTopics.map(topic => (
              <div 
                key={topic.topic_id} 
                className={`topic-card ${topic.status}`}
              >
                <h3>{topic.title}</h3>
                <p>{topic.description}</p>
                
                <div className="topic-meta">
                  <div className="topic-status">
                    Status: <span>{topic.status.replace('_', ' ')}</span>
                  </div>
                  
                  <div className="topic-projects">
                    Projects: 
                    <span className="projects-count">
                      {topic.projects.length}
                    </span>
                  </div>
                </div>
                
                {topic.status !== 'learned' && (
                  <button 
                    onClick={() => handleMarkAsLearned(topic.topic_id)}
                    className="mark-learned-btn"
                  >
                    Mark as Learned
                  </button>
                )}
                
                {/* Placeholder for dependencies visualization */}
                {(topic.prerequisites.length > 0 || topic.dependent_topics.length > 0) && (
                  <div className="topic-relationships">
                    {topic.prerequisites.length > 0 && (
                      <div className="prerequisites">
                        <strong>Prerequisites:</strong> 
                        {topic.prerequisites.join(', ')}
                      </div>
                    )}
                    
                    {topic.dependent_topics.length > 0 && (
                      <div className="dependents">
                        <strong>Dependent Topics:</strong> 
                        {topic.dependent_topics.join(', ')}
                      </div>
                    )}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </section>
    </div>
  );
};

export default MasterBrainPage; 