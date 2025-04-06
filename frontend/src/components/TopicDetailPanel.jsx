import React from 'react';

/**
 * TopicDetailPanel component for showing detailed information about a selected topic
 * 
 * @param {Object} props
 * @param {Object} props.topic - The selected topic object
 * @param {Function} props.onMarkAsLearned - Callback when topic is marked as learned
 * @param {Function} props.onClose - Callback to close the panel
 */
const TopicDetailPanel = ({ 
  topic, 
  onMarkAsLearned = () => {}, 
  onClose = () => {} 
}) => {
  if (!topic) {
    return null;
  }

  return (
    <div className="topic-detail-panel">
      <div className="topic-detail-header">
        <h2>{topic.title || topic.name}</h2>
        <button className="close-btn" onClick={onClose}>×</button>
      </div>
      
      <div className="topic-detail-content">
        <div className="topic-status-badge" data-status={topic.status || 'not_learned'}>
          {topic.status === 'learned' ? 'Learned' : 
           topic.status === 'in_progress' ? 'In Progress' : 'Not Learned'}
        </div>
        
        <div className="topic-description">
          <h3>Description</h3>
          <p>{topic.description || 'No description available.'}</p>
        </div>
        
        {topic.prerequisites && topic.prerequisites.length > 0 && (
          <div className="topic-prerequisites">
            <h3>Prerequisites</h3>
            <ul>
              {topic.prerequisites.map(prereqId => (
                <li key={prereqId}>{prereqId}</li>
              ))}
            </ul>
          </div>
        )}
        
        {topic.dependent_topics && topic.dependent_topics.length > 0 && (
          <div className="topic-dependent-topics">
            <h3>Dependent Topics</h3>
            <ul>
              {topic.dependent_topics.map(depId => (
                <li key={depId}>{depId}</li>
              ))}
            </ul>
          </div>
        )}
        
        {topic.projects && topic.projects.length > 0 && (
          <div className="topic-projects">
            <h3>Related Projects</h3>
            <ul>
              {topic.projects.map(project => (
                <li key={project.id || project}>
                  {project.name || project}
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
      
      <div className="topic-detail-actions">
        {topic.status !== 'learned' && (
          <button 
            className="mark-learned-btn"
            onClick={() => onMarkAsLearned(topic.topic_id)}
          >
            Mark as Learned
          </button>
        )}
      </div>
    </div>
  );
};

export default TopicDetailPanel; 