import { useState } from 'react';
import TopicGraph from './TopicGraph';
import TopicDetailPanel from './TopicDetailPanel';
import './TopicGraph.css';

/**
 * GraphVisualization component that combines the graph visualization with detail panel
 * 
 * @param {Object} props
 * @param {Array} props.topics - Array of topic objects
 * @param {Function} props.onMarkAsLearned - Callback when a topic is marked as learned
 * @param {string} props.height - Height of the graph container (default: '600px')
 */
const GraphVisualization = ({
  topics = [],
  onMarkAsLearned = () => {},
  height = '600px'
}) => {
  const [selectedTopic, setSelectedTopic] = useState(null);
  const [layout, setLayout] = useState('dagre');

  const handleNodeClick = (topicData) => {
    setSelectedTopic(topicData);
  };

  const handleClosePanel = () => {
    setSelectedTopic(null);
  };

  const handleMarkLearned = (topicId) => {
    onMarkAsLearned(topicId);
    // Update local state to immediately reflect change
    if (selectedTopic && selectedTopic.topic_id === topicId) {
      setSelectedTopic({
        ...selectedTopic,
        status: 'learned'
      });
    }
  };

  return (
    <div className="graph-container" style={{ height }}>
      {/* Layout toggle */}
      <div className="graph-layout-toggle">
        <select 
          value={layout}
          onChange={(e) => setLayout(e.target.value)}
        >
          <option value="dagre">Hierarchical Layout</option>
          <option value="cose-bilkent">Force-Directed Layout</option>
        </select>
      </div>
      
      {/* Graph visualization */}
      <TopicGraph 
        topics={topics}
        onNodeClick={handleNodeClick}
        layout={layout}
        height="100%"
      />
      
      {/* Details panel for selected topic */}
      {selectedTopic && (
        <TopicDetailPanel 
          topic={selectedTopic}
          onMarkAsLearned={handleMarkLearned}
          onClose={handleClosePanel}
        />
      )}
      
      {/* Legend */}
      <div className="graph-legend">
        <div className="legend-title">Topic Status</div>
        <div className="legend-item">
          <div className="legend-color learned"></div>
          <span>Learned</span>
        </div>
        <div className="legend-item">
          <div className="legend-color in-progress"></div>
          <span>In Progress</span>
        </div>
        <div className="legend-item">
          <div className="legend-color not-learned"></div>
          <span>Not Learned</span>
        </div>
      </div>
    </div>
  );
};

export default GraphVisualization; 