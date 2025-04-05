import React, { useState, useEffect } from 'react';
import { getMasterGraph } from '../services/api';
import GraphVisualization from '../components/GraphVisualization';
import TopicDetail from '../components/TopicDetail';

const MasterBrainPage = () => {
  const [graphData, setGraphData] = useState({ nodes: [], edges: [] });
  const [selectedTopic, setSelectedTopic] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  // Load master brain data when the component mounts
  useEffect(() => {
    fetchMasterBrain();
  }, []);

  const fetchMasterBrain = async () => {
    try {
      setIsLoading(true);
      const data = await getMasterGraph();
      setGraphData(data);
      setError('');
    } catch (error) {
      console.error('Error fetching master brain:', error);
      setError('Failed to load master brain data. Please try again later.');
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

  return (
    <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '0 20px' }}>
      <div style={{ marginBottom: '30px' }}>
        <h1>Master Brain</h1>
        <p>
          View all programming concepts across all your projects in a single knowledge graph.
        </p>
      </div>
      
      {isLoading ? (
        <div>Loading master brain...</div>
      ) : error ? (
        <div style={{
          padding: '15px',
          backgroundColor: '#f8d7da',
          color: '#721c24',
          borderRadius: '4px',
          marginBottom: '20px'
        }}>
          {error}
          <button
            onClick={fetchMasterBrain}
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
        </div>
      ) : (
        <div style={{ 
          display: 'flex', 
          height: 'calc(100vh - 300px)',
          minHeight: '500px',
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
                <p style={{ 
                  fontSize: '0.9rem', 
                  color: '#6c757d',
                  marginTop: '15px'
                }}>
                  The master brain contains topics from all your projects. 
                  This helps you visualize your entire learning journey and 
                  the connections between different concepts.
                </p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default MasterBrainPage; 