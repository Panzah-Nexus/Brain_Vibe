import React, { useState } from 'react';
import { completeTopic } from '../services/api';

const TopicDetail = ({ topic, onStatusChange }) => {
  const [isUpdating, setIsUpdating] = useState(false);
  
  if (!topic) {
    return null;
  }

  const handleStatusChange = async () => {
    try {
      setIsUpdating(true);
      
      // Toggle the status
      const newStatus = topic.status === 'LEARNED' ? 'NOT_LEARNED' : 'LEARNED';
      
      // Call the API to update the status
      const updatedTopic = await completeTopic(topic.topic_id, newStatus);
      
      // Call the callback to update the UI
      if (onStatusChange) {
        onStatusChange(updatedTopic);
      }
      
      setIsUpdating(false);
    } catch (error) {
      console.error('Error updating topic status:', error);
      setIsUpdating(false);
    }
  };

  return (
    <div style={{
      padding: '20px',
      backgroundColor: '#f8f9fa',
      borderRadius: '8px',
      boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
      marginBottom: '20px'
    }}>
      <h3 style={{ 
        marginTop: 0, 
        color: '#333',
        borderBottom: '1px solid #ddd',
        paddingBottom: '10px'
      }}>
        {topic.display_name}
      </h3>
      
      <div style={{ 
        display: 'flex', 
        alignItems: 'center', 
        marginBottom: '15px',
        justifyContent: 'space-between'
      }}>
        <div>
          <strong>Status:</strong> 
          <span style={{ 
            display: 'inline-block',
            padding: '4px 8px',
            borderRadius: '4px',
            backgroundColor: topic.status === 'LEARNED' ? '#d4edda' : '#f8d7da',
            color: topic.status === 'LEARNED' ? '#155724' : '#721c24',
            marginLeft: '8px'
          }}>
            {topic.status}
          </span>
        </div>
        
        <button
          onClick={handleStatusChange}
          disabled={isUpdating}
          style={{
            padding: '8px 12px',
            borderRadius: '4px',
            border: 'none',
            backgroundColor: topic.status === 'LEARNED' ? '#dc3545' : '#28a745',
            color: 'white',
            cursor: isUpdating ? 'not-allowed' : 'pointer',
            opacity: isUpdating ? 0.7 : 1
          }}
        >
          {isUpdating ? 'Updating...' : (topic.status === 'LEARNED' ? 'Mark as Not Learned' : 'Mark as Learned')}
        </button>
      </div>
      
      {topic.short_description && (
        <div style={{ marginBottom: '15px' }}>
          <strong>Description:</strong>
          <p style={{ marginTop: '5px' }}>{topic.short_description}</p>
        </div>
      )}
      
      {topic.prerequisites && topic.prerequisites.length > 0 && (
        <div>
          <strong>Prerequisites:</strong>
          <ul style={{ marginTop: '5px' }}>
            {topic.prerequisites.map(prereq => (
              <li key={prereq}>{prereq}</li>
            ))}
          </ul>
        </div>
      )}
      
      {topic.projects && topic.projects.length > 0 && (
        <div style={{ marginTop: '15px' }}>
          <strong>Used in Projects:</strong>
          <ul style={{ marginTop: '5px' }}>
            {topic.projects.map(projectId => (
              <li key={projectId}>{projectId}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default TopicDetail; 